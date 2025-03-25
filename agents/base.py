"""
קלאסים בסיסיים למערכת ה-Agents
"""

from openai import OpenAI
from typing import Optional, Any, List, Callable, Dict
from pydantic import BaseModel, create_model
import json
import inspect
import functools

class Agent:
    """מחלקת בסיס לסוכן AI שיכול להשתמש בכלים"""
    
    def __init__(self, client, model="gpt-4o", woo_client=None):
        """
        אתחול סוכן AI בסיסי
        
        Args:
            client: לקוח OpenAI
            model: מודל השפה לשימוש
            woo_client: לקוח WooCommerce (אופציונלי)
        """
        self.client = client
        self.model = model
        self.tools = []
        self.description = None
        self.woocommerce = woo_client  # שמירת לקוח WooCommerce בתכונה
        self.function_map = {}  # מיפוי של פונקציות
    
    def run(self, input_text):
        """
        הפעלת הסוכן עם טקסט קלט
        
        Args:
            input_text: טקסט השאלה/הבקשה
            
        Returns:
            תשובת הסוכן כמחרוזת
        """
        # המרת הכלים לפורמט שמתאים ל-OpenAI API
        tools_for_api = []
        
        for tool in self.tools:
            # התמיכה בהעברה לסוכן אחר
            if isinstance(tool, Handoff):
                tools_for_api.append({
                    "type": "function",
                    "function": {
                        "name": f"handoff_to_{tool.name}",
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "שאלה להעביר לסוכן המקבל"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                })
            # כלים רגילים
            elif isinstance(tool, Tool):
                function_obj = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
                
                # אם יש פרמטרים מוגדרים לכלי, נשתמש בהם
                if tool.parameters:
                    function_obj["parameters"]["properties"] = tool.parameters
                else:
                    # אחרת, נגדיר פרמטר generic
                    function_obj["parameters"]["properties"] = {
                        "input": {
                            "type": "string", 
                            "description": "קלט לפונקציה"
                        }
                    }
                
                tools_for_api.append({
                    "type": "function",
                    "function": function_obj
                })
        
        try:
            # קריאה ל-API עם הכלים
            messages = [{"role": "user", "content": input_text}]
            if self.description:
                messages.insert(0, {"role": "system", "content": self.description})
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_for_api if tools_for_api else None
            )
            
            # אם יש קריאת כלי, מבצע אותה
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                
                # בדיקה אם מדובר בהעברה לסוכן אחר
                if tool_name.startswith("handoff_to_"):
                    for tool in self.tools:
                        if isinstance(tool, Handoff) and tool_name == f"handoff_to_{tool.name}":
                            # הפעלת הסוכן המקבל עם השאלה שהועברה
                            try:
                                args = json.loads(tool_call.function.arguments)
                                if isinstance(args, dict) and "query" in args:
                                    return tool.agent.run(args["query"])
                                else:
                                    return tool.agent.run(str(args))
                            except json.JSONDecodeError:
                                return tool.agent.run(tool_call.function.arguments)
                
                # הפעלת כלי רגיל
                for tool in self.tools:
                    if isinstance(tool, Tool) and tool.name == tool_name:
                        try:
                            args = json.loads(tool_call.function.arguments)
                            # בדיקה אם args הוא מילון
                            if isinstance(args, dict):
                                if "input" in args:
                                    tool_result = tool(args["input"])
                                else:
                                    tool_result = tool(args)  # העבר את כל הארגומנטים
                            else:
                                tool_result = tool(args)  # העבר את הארגומנטים כמו שהם
                        except json.JSONDecodeError:
                            # אם יש בעיה בפענוח ה-JSON, העבר את הארגומנטים כמחרוזת
                            tool_result = tool(tool_call.function.arguments)
                        
                        try:
                            # שליחת התוצאה חזרה ל-API
                            final_messages = messages.copy()
                            final_messages.append({
                                "role": "assistant", 
                                "content": None, 
                                "tool_calls": [
                                    {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {
                                            "name": tool_name,
                                            "arguments": tool_call.function.arguments
                                        }
                                    }
                                ]
                            })
                            final_messages.append({
                                "role": "tool", 
                                "tool_call_id": tool_call.id, 
                                "content": str(tool_result)
                            })
                            
                            final_response = self.client.chat.completions.create(
                                model=self.model,
                                messages=final_messages
                            )
                            return final_response.choices[0].message.content
                        except Exception as e:
                            return f"שגיאה בעיבוד תוצאות הכלי: {str(e)}\n\nהנה התוצאות הגולמיות:\n{tool_result}"
            
            # אם אין קריאת כלי, מחזיר את התשובה כמו שהיא
            return message.content or "לא התקבלה תשובה מהמודל"
            
        except Exception as e:
            return f"שגיאה בהפעלת הסוכן: {str(e)}"
        
    def add_tool(self, tool_or_fn):
        """
        הוספת כלי לסוכן
        
        Args:
            tool_or_fn: כלי (Tool) או פונקציה מעוטרת ב-@function_tool
        """
        # אם קיבלנו פונקציה מעוטרת
        if hasattr(tool_or_fn, 'tool'):
            tool = tool_or_fn.tool
        # אם קיבלנו כלי ישירות
        elif isinstance(tool_or_fn, (Tool, Handoff)):
            tool = tool_or_fn
        else:
            raise ValueError(f"הפרמטר tool_or_fn חייב להיות פונקציה מעוטרת ב-@function_tool או אובייקט מסוג Tool, קיבלנו {type(tool_or_fn)}")
        
        self.tools.append(tool)
        
        # הוספת מתודה לקריאה ישירה של הכלי
        if isinstance(tool, Tool):
            # יצירת פונקציה שתעטוף את הקריאה לכלי
            def wrapper_method(*args, **kwargs):
                return tool(*args, **kwargs)
            
            # הוספת המתודה לסוכן
            setattr(self, tool.name, wrapper_method)
            
            # הוספה למיפוי פונקציות
            self.function_map[tool.name] = wrapper_method
        
        return self

class Handoff:
    """Base class for agent handoffs"""
    def __init__(self, name: str, agent: Agent, description: str):
        self.name = name
        self.agent = agent
        self.description = description
        
    def run(self, user_input: str) -> str:
        """
        מעביר את הבקשה לסוכן המתמחה ומחזיר את התשובה
        
        Args:
            user_input: קלט המשתמש
            
        Returns:
            str: תשובת הסוכן המתמחה
        """
        return self.agent.run(user_input)

class Guardrail:
    """Base class for agent guardrails"""
    def __init__(self, client: OpenAI, model: str, instructions: str):
        self.client = client
        self.model = model
        self.instructions = instructions
    
    def check(self, input_text: str) -> bool:
        """Check if the input passes the guardrail"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": input_text}
            ]
        )
        return "true" in response.choices[0].message.content.lower()

class Thread:
    """Base class for agent threads"""
    def __init__(self):
        self.messages: List[dict] = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

class Runner:
    """Base class for running agents"""
    @staticmethod
    def run(agent: Agent, user_input: str) -> Any:
        return agent.run(user_input)

class Tool:
    """Base class for agent tools"""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = None
    
    def __call__(self, *args, **kwargs) -> Any:
        """Call the tool with the given arguments"""
        try:
            # אם קיבלנו ארגומנט אחד שהוא מחרוזת, ננסה לפענח אותו כ-JSON
            if len(args) == 1 and isinstance(args[0], str) and not kwargs:
                try:
                    # מנסה לפרש כ-JSON
                    parsed_args = json.loads(args[0])
                    if isinstance(parsed_args, dict):
                        # אם קיבלנו מילון, נעביר אותו כפרמטרים לפונקציה
                        return self.func(**parsed_args)
                    else:
                        # אם קיבלנו ערך אחר, נעביר אותו כמו שהוא
                        return self.func(parsed_args)
                except json.JSONDecodeError:
                    # אם זו לא מחרוזת JSON תקינה, נעביר אותה כמו שהיא
                    return self.func(args[0])
            # אם קיבלנו מילון, נעביר אותו כפרמטרים לפונקציה
            elif len(args) == 1 and isinstance(args[0], dict) and not kwargs:
                return self.func(**args[0])
            else:
                # אחרת, נעביר את כל הפרמטרים כרגיל
                return self.func(*args, **kwargs)
        except Exception as e:
            return f"שגיאה בהפעלת הכלי: {str(e)}"

def function_tool(fn=None, *, name=None, description=None):
    """
    מעטר פונקציה כדי להפוך אותה לכלי שימושי.
    
    Args:
        fn: פונקציה לעטר
        name: שם הכלי (ברירת מחדל: שם הפונקציה)
        description: תיאור הכלי (ברירת מחדל: ה-docstring של הפונקציה)
    
    Returns:
        הפונקציה המעוטרת
    """
    def decorator(func):
        # שימוש בשם הפונקציה אם לא סופק שם
        tool_name = name or func.__name__
        
        # שימוש ב-docstring של הפונקציה אם לא סופק תיאור
        tool_description = description or func.__doc__ or f"הפעל את הפונקציה {tool_name}"
        
        # איסוף פרמטרים של הפונקציה (פרט ל-woo_client)
        sig = inspect.signature(func)
        parameters = {}
        for param_name, param in sig.parameters.items():
            if param_name != 'woo_client':  # דילוג על woo_client
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any

                # המרת טיפוסי Python לטיפוסי JSON Schema
                json_schema_type = "string"  # ברירת מחדל
                
                if param_type == int:
                    json_schema_type = "integer"
                elif param_type == str:
                    json_schema_type = "string"
                elif param_type == bool:
                    json_schema_type = "boolean"
                elif param_type == float:
                    json_schema_type = "number"
                elif param_type == list or param_type == tuple:
                    json_schema_type = "array"
                elif param_type == dict:
                    json_schema_type = "object"
                elif param_type == Any:
                    json_schema_type = "string"
                
                # הוספת מידע על פרמטר
                parameters[param_name] = {
                    "type": json_schema_type
                }
                
                # הוספת מידע נוסף לפי טיפוס הפרמטר
                if json_schema_type == "array":
                    # לכל מערך צריך להיות מבנה items
                    parameters[param_name]["items"] = {"type": "string"}
                
                elif json_schema_type == "object":
                    # לכל אובייקט מאפשרים מפתחות נוספים
                    parameters[param_name]["additionalProperties"] = True
                
                # הוספת ערכי ברירת מחדל אם יש
                if param.default != inspect.Parameter.empty:
                    if param.default is not None:
                        parameters[param_name]["default"] = param.default
        
        # יצירת כלי ושמירתו כתכונה של הפונקציה
        tool = Tool(tool_name, tool_description, func)
        func.tool = tool
        
        # הוספת פרמטרים לכלי
        if parameters:
            tool.parameters = parameters
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.tool = tool
        return wrapper
    
    # טיפול במקרה שהמעטר מופעל עם או בלי פרמטרים
    if fn is None:
        return decorator
    else:
        return decorator(fn) 
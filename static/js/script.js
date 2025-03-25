// משתנים גלובליים
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const suggestionContainer = document.createElement('div');
suggestionContainer.className = 'suggestion-container';
let isWaitingForResponse = false;

// הצעות נפוצות לשימוש
const commonSuggestions = [
    "צור מוצר חדש",
    "עדכן מלאי של מוצר",
    "הצג רשימת מוצרים",
    "מצא מוצר לפי שם",
    "עדכן מחיר של מוצר"
];

// פונקציה לאתחול הצעות
function initSuggestions() {
    suggestionContainer.innerHTML = '';
    
    // הוספת כותרת להצעות
    const title = document.createElement('div');
    title.className = 'suggestion-title';
    title.textContent = 'פעולות נפוצות:';
    suggestionContainer.appendChild(title);

    // הוספת כפתורי הצעות
    commonSuggestions.forEach(suggestion => {
        const suggestionBtn = document.createElement('button');
        suggestionBtn.className = 'suggestion-btn';
        suggestionBtn.textContent = suggestion;
        suggestionBtn.addEventListener('click', () => {
            userInput.value = suggestion;
            userInput.focus();
        });
        suggestionContainer.appendChild(suggestionBtn);
    });

    // הוספת הצעות מתחת לטופס
    chatForm.parentNode.insertBefore(suggestionContainer, chatForm.nextSibling);
}

// הוספת הודעת ברוכים הבאים עם הוראות
function addWelcomeMessage() {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'message bot';
    
    const welcomeContent = document.createElement('div');
    welcomeContent.className = 'message-content';
    welcomeContent.innerHTML = `
        <strong>ברוכים הבאים ל-WooCommerce AI Agent!</strong><br>
        אני יכול לעזור לך בניהול חנות WooCommerce שלך. הנה כמה דוגמאות לבקשות:
        <ul>
            <li>"צור מוצר חדש בשם 'חולצה כחולה' עם מחיר 99.90"</li>
            <li>"עדכן את המלאי של מוצר עם מזהה 123 לכמות 50"</li>
            <li>"הצג את רשימת המוצרים בחנות"</li>
        </ul>
        ניתן גם ללחוץ על אחת ההצעות למטה כדי להתחיל.
    `;
    
    welcomeDiv.appendChild(welcomeContent);
    chatMessages.appendChild(welcomeDiv);
    
    // גלילה לתחתית הצ'אט
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// האזנה לשליחת טופס
chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (message === '') return;
    
    // הצגת הודעת משתמש
    addMessage(message, 'user');
    
    // ניקוי תיבת הקלט
    userInput.value = '';
    
    // אם כבר מחכים לתשובה, לא לשלוח בקשה נוספת
    if (isWaitingForResponse) return;
    
    // הצגת אינדיקטור טעינה
    showTypingIndicator();
    
    // שליחת ההודעה לשרת
    sendMessageToServer(message);
});

// פונקציה להוספת הודעה לחלון הצ'אט
function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // גלילה לתחתית הצ'אט
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// פונקציה להצגת אינדיקטור טעינה
function showTypingIndicator() {
    isWaitingForResponse = true;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typing-indicator';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'message-content';
    
    // הוספת טקסט "אנא המתן..." עם אנימציית נקודות
    typingContent.innerHTML = "אנא המתן, מעבד את הבקשה שלך";
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        typingIndicator.appendChild(dot);
    }
    
    typingContent.appendChild(typingIndicator);
    typingDiv.appendChild(typingContent);
    chatMessages.appendChild(typingDiv);
    
    // גלילה לתחתית הצ'אט
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// פונקציה להסרת אינדיקטור טעינה
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isWaitingForResponse = false;
}

// פונקציה לשליחת הודעה לשרת
async function sendMessageToServer(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });
        
        const data = await response.json();
        
        // הסרת אינדיקטור טעינה
        removeTypingIndicator();
        
        if (data.error) {
            // הצגת שגיאה
            addMessage(`שגיאה: ${data.error}`, 'bot');
        } else {
            // הצגת תשובת הבוט
            addFormattedResponse(data.response);
        }
    } catch (error) {
        // הסרת אינדיקטור טעינה
        removeTypingIndicator();
        
        // הצגת שגיאה
        addMessage('אירעה שגיאה בתקשורת עם השרת. נסה שוב מאוחר יותר.', 'bot');
        console.error('Error:', error);
    }
}

// פונקציה להצגת תשובה מפורמטת
function addFormattedResponse(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // המרת שורות חדשות ל-<br>
    const formattedText = response.replace(/\n/g, '<br>');
    messageContent.innerHTML = formattedText;
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // גלילה לתחתית הצ'אט
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// פוקוס על תיבת הקלט בטעינת הדף
window.addEventListener('load', function() {
    userInput.focus();
    initSuggestions();
    
    // בדיקה אם זה הרינדור הראשוני של הדף
    if (chatMessages.childElementCount <= 1) {
        addWelcomeMessage();
    }
}); 
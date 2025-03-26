import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
  
  // לא יגיע לכאן בגלל ההפניה, אבל Next.js דורש שיהיה ערך מוחזר מהפונקציה
  return null;
}

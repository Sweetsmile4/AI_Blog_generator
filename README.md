# AI_Blog_generator

The **AI Blog Generator** is an intelligent web application that converts any YouTube video link into a well-structured **blog**, along with **summaries, transcripts, and notes** — all powered by **AI**.

This project demonstrates the integration of **AI automation**, **backend processing**, and **frontend interactivity** in one full-stack system.

---

## 🚀 Features

- 🎥 **YouTube to Blog Conversion** – Generates full-length, AI-written blogs from YouTube videos.  
- 🗒️ **Video Transcript & Summary** – Extracts and summarizes transcripts using AI.  
- 🧩 **Blog Management** – Includes sections like *All Blogs* and *Blog Details*.  
- 💬 **Chat History System** – Saves generated content and user interactions.  
- 🔐 **User Authentication** – Login and Sign-Up system for managing user accounts.  
- 🧠 **AI-Powered Automation** – Uses APIs (like OpenAI & AssemblyAI) for text generation and analysis.

---

## 🧰 Tech Stack

| Area | Technology |
|------|-------------|
| Frontend | React.js / HTML / CSS |
| Backend | Node.js / Express.js |
| Database | MySQL |
| AI Integration | OpenAI API, AssemblyAI |
| Authentication | JWT / bcrypt |
| Hosting (optional) | Localhost / Render / Vercel |

---

## ⚙️ How It Works

1. User pastes a YouTube video link.  
2. The backend fetches and transcribes the video using **AssemblyAI**.  
3. The transcript is processed by **OpenAI API** to generate:  
   - Summary  
   - Full-length blog  
   - Notes  
4. Data is stored in **MySQL**, and users can view all blogs or specific details.  

---

## 📸 Project Screens (optional)
*(Add screenshots here later, like login page, blog list, and generated blog)*

---

## 🧑‍💻 Setup & Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/ai-blog-generator.git

# Navigate to project folder
cd ai-blog-generator

# Install dependencies
npm install

# Start the backend
cd server
npm start

# Start the frontend
cd client
npm start

💡 Make sure you add your own API keys (OpenAI, AssemblyAI) in a .env file.

---

## 🔑 Environment Variables

Create a .env file in the root directory and add:

OPENAI_API_KEY=your_openai_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_blog
JWT_SECRET=your_secret

🧩 Future Enhancements

Add dark/light mode support 🌙

Enable blog editing and deletion ✏️

Include AI-generated thumbnails 🖼️

Deploy with cloud storage integration ☁️




⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub — it motivates further development!

# AI Image Grouper

A smart web application that organizes your image collections by content similarity using Google's Gemini AI.

## 🚀 Overview

AI Image Grouper allows users to upload a batch of images and automatically groups them based on their visual content. It leverages the power of the **Gemini 2.5 Flash Lite** model to understand the image content and **Text Embedding 004** to calculate semantic similarities.

## ✨ Features

*   **Multi-Image Upload:** Select and upload multiple images at once.
*   **AI-Powered Analysis:** Uses Google's Gemini Vision model to generate detailed descriptions of each image.
*   **Intelligent Grouping:** Clusters images with similar content using cosine similarity on text embeddings.
*   **Visual Gallery:** Displays the grouped images in a clean, organized grid.
*   **Parallel Processing:** Efficiently handles multiple images using concurrent processing.

## 🛠️ Tech Stack

*   **Backend:** Python, Flask, Google Generative AI SDK, NumPy
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript
*   **AI Models:**
    *   Vision: `gemini-2.5-flash-lite`
    *   Embedding: `models/text-embedding-004`

## 📋 Prerequisites

Before running this project, ensure you have the following:

*   **Python 3.8+** installed on your machine.
*   A **Google Gemini API Key**. You can get one from [Google AI Studio](https://aistudio.google.com/).

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ELHILALICODE/ai-image-grouper.git
cd ai-image-grouper
```

### 2. Backend Setup

Navigate to the `backend` directory and install the required dependencies.

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the Server

Start the Flask backend server:

```bash
python server.py
```

The server will start running on `http://localhost:3000`.

### 4. Frontend Setup

Since this is a simple static frontend, you can open it directly in your browser or serve it using a lightweight server.

**Option A: Open directly**
Navigate to the `frontend` folder and double-click `index.html` to open it in your browser.

**Option B: Using Python (Recommended)**
In a separate terminal, run:

```bash
cd frontend
python -m http.server 8000
```
Then open `http://localhost:8000` in your browser.

*Note: The frontend is configured to send requests to the backend at `http://localhost:3000`.*

## 📖 Usage

1.  Open the application in your web browser.
2.  Click the **"Choose Files"** button or input area and select a batch of images (e.g., a mix of cat, dog, and car photos).
3.  Click **"Process Images"**.
4.  Wait for the AI to analyze and group your images.
5.  View the results in the "Image Groups" section below.

## 📂 Project Structure

```
ai_001/
├── backend/
│   ├── uploads/          # Stores uploaded images
│   ├── .env              # Environment variables (API Key)
│   ├── server.py         # Flask backend logic
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Main UI
│   ├── script.js         # Frontend logic & API calls
│   └── styles.css        # Styling
└── README.md             # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

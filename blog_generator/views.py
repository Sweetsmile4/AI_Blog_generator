from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os
import assemblyai as aai
from .models import BlogPost
from dotenv import load_dotenv
import logging
import yt_dlp
from groq import Groq

load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            print(f"Received YouTube link: {yt_link}")
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        try:
            title = yt_title(yt_link)
            print(f"Extracted YouTube title: {title}")
        except Exception as e:
            logger.error(f"Error fetching YouTube title: {e}")
            return JsonResponse({'error': 'Failed to fetch YouTube title'}, status=500)

        try:
            transcription = get_transcription(yt_link)
            print(f"Transcription received: {transcription[:100]}")  # Log first 100 chars
        except Exception as e:
            logger.error(f"Error fetching transcription: {e}")
            return JsonResponse({'error': 'Failed to get transcription'}, status=500)

        try:
            blog_content = generate_blog_from_transcription(transcription)
            print(f"Generated blog content: {blog_content[:100]}")  # Log first 100 chars
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            return JsonResponse({'error': 'Failed to generate blog article'}, status=500)

        try:
            new_blog_article = BlogPost.objects.create(
                user=request.user,
                youtube_title=title,
                youtube_link=yt_link,
                generated_content=blog_content,
            )
            new_blog_article.save()
        except Exception as e:
            logger.error(f"Error saving blog post to database: {e}")
            return JsonResponse({'error': 'Failed to save blog article'}, status=500)

        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def yt_title(link):
    video_id = link.split("v=")[-1]  # Extract video ID from link
    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            title = data['items'][0]['snippet']['title']
            return title
        except (IndexError, KeyError):
            return "Title not available"
    else:
        return f"Error fetching title: {response.status_code}"


def download_audio(link):
    try:
        # Ensure media directory exists
        media_dir = "media/"
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(media_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            mp3_file = os.path.splitext(filename)[0] + '.mp3'
            if os.path.exists(mp3_file):
                print(f"Downloaded and converted to mp3: {mp3_file}")
                return mp3_file
            else:
                logger.error("yt-dlp did not produce an mp3 file.")
                print("yt-dlp did not produce an mp3 file.")
                return None
    except Exception as e:
        logger.error(f"yt-dlp audio download error: {e}")
        print(f"yt-dlp audio download error: {e}")
        return None


def get_transcription(link):
    audio_file = download_audio(link)
    if not audio_file:
        logger.error("Audio file could not be downloaded. Skipping transcription.")
        return "Error: Audio file could not be downloaded."
    aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")

    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        return transcript.text
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return f"Error during transcription: {e}"


def generate_blog_from_transcription(transcription):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = (
        "You are a blog writer. Based on the following transcript from a YouTube video, "
        "write a comprehensive blog article. "
        "⚡ Format the output strictly in HTML. "
        "⚡ Use <h2> for main headings, <h3> for subheadings, <p> for paragraphs, "
        "and <ul><li> for bullet points or lists. "
        "⚡ Use <strong> for bold text instead of **markdown**. "
        "⚡ Do not include Markdown symbols like ** or ###. "
        "⚡ Ensure clean, well-structured formatting with separate paragraphs.\n\n"
        f"{transcription}\n\nHTML Article:"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast, free Groq model
            messages=[
                {"role": "system", "content": "You write professional, structured blog articles in clean HTML."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        generated_content = response.choices[0].message.content.strip()
        return generated_content

    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        return f"Groq API Error: {e}"



def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})


def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')


def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except Exception as e:
                logger.error(f"Error creating account: {e}")
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})
        
    return render(request, 'signup.html')


def user_logout(request):
    logout(request)
    return redirect('/')

# All modules necessary for Django to work + extra
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AudiofySignupForm
from django.db.models import Q
# All modules necessary for Photo Uploading and AWS storage uploading
import uuid
import boto3

from .models import Playlist, Song

# We will need this once we need to add more forms for songs under playlists
# from .forms import SomeForm

# Things we will need once we set up AWS
# S3_BASE_URL = 's3.ca-central-1.amazonaws.com/'
# BUCKET = 'needtosetup'


def landing_page(request):
  return render(request, 'landing_page.html')

class PlaylistCreate(LoginRequiredMixin, CreateView):
  model = Playlist
  fields = ['title', 'description']

  def form_valid(self, form):
    form.instance.user = self.request.user  
    return super().form_valid(form)

class PlaylistUpdate(LoginRequiredMixin, UpdateView):
  model = Playlist
  fields = ['title', 'description']

class PlaylistDelete(LoginRequiredMixin, DeleteView):
  model = Playlist
  success_url = '/playlists'

@login_required
def playlist_detail(request, playlist_id):
  playlist = Playlist.objects.get(id=playlist_id)
  songs_not_added = Song.objects.exclude(id__in = playlist.songs.all().values_list('id'))
  return render(request, 'playlist/detail.html', {
    'playlist': playlist, 
    'songs': songs_not_added,
  })

@login_required
def playlist_index(request):
  first_name = request.user.first_name
  last_name = request.user.last_name
  username = request.user.username
  playlists = Playlist.objects.filter(user=request.user)
  return render(request, 'playlist/index.html', { 'playlists': playlists, "username": username, "first_name": first_name, "last_name": last_name})

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = AudiofySignupForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = AudiofySignupForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

# Associating Songs with Playlist
def assoc_song(request, song_id, playlist_id):
  Playlist.objects.get(id=playlist_id).songs.add(song_id)
  return redirect('songs_index')

def unassoc_song(request, song_id, playlist_id):
  Playlist.objects.get(id=playlist_id).songs.remove(song_id)
  return redirect('songs_index')

class SongList(ListView):
  model = Song

@login_required
def songs_index(request):
  first_name = request.user.first_name
  playlists = Playlist.objects.filter(user=request.user)
  if request.method == 'POST':
      query = request.POST.get('q')
      object_list = Song.objects.filter(
        Q(title__icontains=query) | Q(createdby__icontains=query)
      )
      songs = object_list
  else: 
    songs = Song.objects.all()
  return render(request, 'song/songs.html', {'first_name': first_name, 'songs':songs, 'playlists':playlists})

@login_required
def song_detail(request, song_id):
  song = Song.objects.get(id=song_id)
  return render(request, 'song/song_details.html',{
    'song': song
  })
  

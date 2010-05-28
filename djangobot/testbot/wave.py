from waveapi import events
from waveapi import robot
from waveapi import django_robot_runner
import logging
import credentials

def OnWaveletSelfAdded(event, wavelet):
  """Invoked when the robot has been added."""
  logging.info("OnWaveletSelfAdded called")
  wavelet.reply("\nHi everybody! I'm a Python DJANGO robot!")
  
def OnWaveletParticipantsChanged(event, wavelet):
  logging.info("OnParticipantsChanged called")
  newParticipants = event.participants_added
  for newParticipant in newParticipants:
    wavelet.reply("\nHi : " + newParticipant)

def OnWaveAnything(request):
  myRobot = robot.Robot('Django bot', 
      image_url='http://nedbatchelder.com/pix/django-icon-256.png',
      profile_url='http://www.django.com')
  myRobot.register_handler(events.WaveletParticipantsChanged, OnWaveletParticipantsChanged)
  myRobot.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
  myRobot.set_verification_token_info(credentials.VER, credentials.ST)
  myRobot.setup_oauth(credentials.KEY, credentials.SECRET, server_rpc_base='http://www-opensocial-sandbox.googleusercontent.com/api/rpc')
  return django_robot_runner.handle(request, myRobot)



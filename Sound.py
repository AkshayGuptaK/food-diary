"""Specifies the sounds to be played for various application triggers"""

import winsound

def play_asterisk_sound():
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
	
def play_exclamation_sound():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
	
def play_critical_stop_sound():
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
	
def play_error_sound():
    winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
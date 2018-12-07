
def get_salutations(lang):
    if lang == 'english':
        return ["hi", "dear", "to", "hey", "hello", "thanks", "good morning",
                "good afternoon", "good evening", "thankyou", "thank you"]

    if lang == 'dutch':
        return ['Doeg', 'Goedemorgen', 'Goedemiddag', 'Goedenavond',
                'Goedenacht', 'Goedendag', 'Goeiendag', 'Gedag', 'Hallo',
                'Dag', 'Hoi', 'Houdoe', 'Geachte', 'Lieve', 'Beste']


def get_signature(lang):
    if lang == 'english':
        return ["warm regards", "kind regards", "regards", "cheers",
                "many thanks", "thanks", "sincerely", "ciao", "Best", "bGIF",
                "thank you", "thankyou", "talk soon", "cordially",
                "yours truly", "thanking You", "sent from my iphone"]

    if lang == 'dutch':
        return ['met vriendelijke groet', 'hoogachtend', 'namens', 'groetjes',
                'groeten', 'vriendelijke groeten', 'dank', 'bedankt', 'vriendelijke groet', 'alvast bedankt', 'mvg', 'gr']
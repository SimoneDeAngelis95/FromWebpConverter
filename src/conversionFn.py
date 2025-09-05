from PIL import Image, ImageSequence

def convertFile(image, pathToSave):
    
    img = Image.open(image)
    name = pathToSave + "/" + extractFileName(image)

    if isGif(image):
        name = name + ".gif"
        img.save(name, format='PNG', save_all=True, lossless=True) # se uso come formato PNG funziona tutto bene
    elif hasAlphaChannel(image):
        name = name + ".png"
        img.save(name, format='PNG', lossless=True)
    else:
        name = name + ".jpg"
        img.save(name, format='JPEG', quality=95) # la documentazione consiglia di usare 95 per avere una riproduzione esatta dell'originale, è comunque la qualità massima disponibile. Se metti 100 hai qualche problema di sgranatura, leggi la documentazione
        
    img.close()

def isGif(filePath):
    try:
        MediaFile = Image.open(filePath)
        Index = 0
        
        for Frame in ImageSequence.Iterator(MediaFile): # conto i frame del file
            Index += 1
        
        if Index > 1:               # se ha più di un frame è una gif
            return True
        else:                       # se ha un solo frame è una semplice foto
            return False
    except:                         # se non è ne l'uno ne l'altra genera un errore
        return False

def extractFileName(filePath):
    name = ""
    i = len(filePath) - 1

    while i >= 0:
        if filePath[i] == ".":
            i = i - 1
            while filePath[i] != "/" and i >= 0:
                name = filePath[i] + name
                i = i - 1
            break
        i = i - 1
    return name

def hasAlphaChannel(file):
    img = Image.open(file)
    
    if img.info.get("transparency", None) is not None: # se nelle info dell'immagine c'è scritto che è presente la trasparenza
        img.close()
        return True
    elif img.mode == "RGBA": # un pò grossolano ed approssimativo, si può migliorare
        img.close()
        return True
    else:
        img.close()
        return False
import xbmcplugin
import xbmcgui
import sys

def list_items():
    # Aquí defines los items que quieres mostrar
    items = [
        {'title': 'Item 1', 'url': 'http://example.com/video1'},
        {'title': 'Item 2', 'url': 'http://example.com/video2'},
    ]
    
    for item in items:
        # Creamos una lista con los items que se mostrarán en Kodi
        li = xbmcgui.ListItem(item['title'], iconImage="th.jpg", thumbnailImage="th.jpg")
        url = item['url']
        
        # Enviar el item al plugin para que se muestre
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

def main():
    # Configuración del handle del addon
    global addon_handle
    addon_handle = int(sys.argv[1])
    
    # Mostrar los items
    list_items()
    
    # Finalizar y mostrar el directorio
    xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
    main()

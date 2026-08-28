#!/system/bin/sh
# ¿Se puede tocar la camara sin molestar? Devuelve 0 si si, 1 si no.
#
# Solo puede haber un cliente de camara a la vez: si dos apps la abren, fallan
# las dos. Y aunque este libre, tampoco hay que meterse si el movil lo esta
# usando alguien en ese momento.
#
# Uso:  sh camara_libre.sh && ...lo que sea...
#       sh camara_libre.sh -f   (ignora que la pantalla este encendida)

# Solo la lista de clientes activos: el volcado tambien trae un historico de
# aperturas viejas que no significa que la camara siga ocupada.
activos=$(dumpsys media.camera 2>/dev/null \
    | sed -n '/Active Camera Clients:/,/^$/p' \
    | grep -o "Client Package Name: [^,]*")
if [ -n "$activos" ]; then
    echo "OCUPADA por $activos"
    exit 1
fi

if [ "$1" != "-f" ] && dumpsys power 2>/dev/null | grep -q "mWakefulness=Awake"; then
    echo "EN USO: la pantalla esta encendida, puede haber alguien delante"
    echo "  $(dumpsys window 2>/dev/null | grep -m1 mCurrentFocus)"
    exit 1
fi

echo "LIBRE"
exit 0

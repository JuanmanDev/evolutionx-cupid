# Apps de banca (Deutsche Bank) en una ROM custom

*Versión en inglés (principal): [`BANK.md`](BANK.md).*

Informe de campo, medido en este propio móvil, sobre las dos apps de Deutsche
Bank en esta ROM:

- **`com.db.pbc.mibanco`** — la app principal ("DB mibanco").
- **`com.db.coo.secureauthenticator`** — el 2FA ("DB Secure Authenticator"), que
  aprueba inicios de sesión y transferencias.

En una línea: **quitar el root hace que la app principal vuelva a funcionar; la
app de 2FA la bloquea la atestación por hardware, no el root, y esa barrera no se
puede levantar con el bootloader desbloqueado sin manipular los controles de
integridad del banco — cosa que este proyecto no va a hacer.**

## Por qué el root era el primer sospechoso, y por qué queda descartado

Con el boot de **KernelSU** las apps fallaban. La causa es la propia capa
anti-manipulación de la app (RASP — Runtime Application Self-Protection). La app
principal escribe sus veredictos al log, y con root presente marcaba el dispositivo.

Con el boot **sin root** (`boot-noksu.img`) esa misma RASP informa de un
dispositivo limpio. Medido, en vivo, en este teléfono:

```
RASPPlugin: notify: ROOTING Detected at observable
Json Result rooting: {"eventType":"ROOTING","data":"{DeviceRootingChanges=5, DeviceRooted=false}"}
Json Result rooting: {"eventType":"FILESYSTEM_SCANNING","data":"{SuspiciousFileDetected=false, SUPermissionDetected=false, SuidOrSgidDetected=false}"}
```

`DeviceRooted=false`, sin `su`, sin ficheros sospechosos, sin SUID/SGID. El propio
detector del banco confirma que el dispositivo no está rooteado. **Eso era lo que
detectaba, y ya no está.**

El propio `su` lo confirma — en el boot sin root la shell no tiene `su`:

```
$ su
/system/bin/sh: su: inaccessible or not found
```

## Lo que funciona

**`com.db.pbc.mibanco` (app principal): funciona.** Arranca, su RASP hace el barrido
completo (root, ficheros, screen-mirroring, lector de pantalla, teclado), llama a
SafetyNet, y sigue hasta cargar el perfil de usuario y sus pantallas normales. Sin
cerrarse, sin bloqueo. La ventana es `FLAG_SECURE` (las capturas salen en negro —
es la app ocultándose de la captura, no un fallo).

Dos avisos **informativos** que levanta la RASP — ninguno bloquea la app:

- `UntrustedScreenreaderPresent=true` — por el **servicio de accesibilidad de
  Lawnchair** (`app.lawnchair/...LawnchairAccessibilityService`), el único servicio
  de accesibilidad activo. Lawnchair lo usa para gestos como doble toque para
  bloquear. Si quieres quitar ese aviso, desactiva la accesibilidad de Lawnchair en
  *Ajustes → Accesibilidad* (pierdes el gesto). La app funciona igual.
- `KeyboardTrusted=false` para **Gboard** — la RASP no se fía de teclados de terceros
  para datos sensibles y prefiere su propio teclado interno. No hay nada que
  arreglar; es informativo.

## Lo que no funciona, y por qué

**`com.db.coo.secureauthenticator` (2FA): bloqueada.** Arranca y se queda en el
splash indefinidamente. Ni se cierra ni llega a la pantalla de acceso. La causa
**no** es el root — es su capa de atestación fallando:

- Su llamada de atestación a Google Play Services devuelve
  `ConnectionResult{statusCode=DEVELOPER_ERROR}`.
- Corre un sandbox de seguridad nativo en un **proceso aislado** que se reapea una
  y otra vez; el proceso principal se queda en bucle en una llamada binder de una
  vía que falla con `error -74` (`EBADMSG`) — "Too many transaction errors".
- Su código anti-bypass vigila específicamente **TrickyStore** (una herramienta de
  spoofing de atestación) en GMS, Play Store y los paquetes del banco, y se niega a
  seguir cuando el entorno no puede producir una atestación real y válida.

Con el **bootloader desbloqueado** — que toda ROM custom exige — Play Integrity /
key attestation no puede dar un veredicto de integridad *de dispositivo*. La app
principal lo tolera y tira de sus propias comprobaciones; la de 2FA no. Exige sí o
sí una atestación por hardware que pase.

### Por qué "funcionaba en EvolutionX 16"

Lo más probable es que el Secure Authenticator fuera una **versión más antigua**
entonces, antes de que Deutsche Bank lo endureciera para exigir integridad de
dispositivo, o que el 2FA se hiciera de otra forma (photoTAN por otra vía, o SMS).
Mismo bootloader desbloqueado, app más estricta hoy. Merece la pena confirmarlo
comparando la versión instalada de la app.

## Lo que este proyecto no va a hacer

Hacer que la app de 2FA pase exigiría **falsear la atestación por hardware** —
instalar TrickyStore más un keybox válido (normalmente filtrado) para que la app
crea que el bootloader está bloqueado. Eso es saltarse a propósito un control de
integridad de un banco en una app financiera, y queda fuera del alcance aquí.
Tampoco se parchea el APK.

## Opciones realistas

1. **Usar la app principal** para consultar y para la mayoría de operaciones, y
   completar el 2FA por un método que no dependa de la atestación del Secure
   Authenticator (p. ej. photoTAN en un segundo móvil de stock, o SMS-TAN si tu
   cuenta lo permite).
2. **Un segundo móvil de stock (bootloader bloqueado)** solo para el Secure
   Authenticator. Es la forma limpia de tener aquí la ROM custom y el 2FA de DB.
3. **Volver este móvil a MIUI/HyperOS de stock y rebloquear el bootloader** si el
   soporte completo de DB en *este* móvil es un requisito duro. Renuncias a la ROM
   custom.
4. **Certificar este dispositivo con Google** (enviar el GSF Android ID en
   `google.com/android/uncertified`). Puede arreglar la integridad *básica* y algún
   error de GMS, pero **no** la integridad de dispositivo/fuerte que la app de 2FA
   necesita con el bootloader desbloqueado. Probarlo no hace daño; no esperes que
   desbloquee el authenticator.

## ¿En qué boot estoy?

- En el boot **sin root** (`boot-noksu.img`), `su` responde
  `inaccessible or not found`, y la RASP de la app principal de DB informa
  `DeviceRooted=false`. Es el boot que hay que usar para banca.
- Para cambiar: `fastboot flash boot boot-noksu.img` (o usa
  `scripts/flashear_todo.sh --no-ksu`). Para volver al root:
  `fastboot flash boot boot-ksu.img`. Tus apps y datos quedan intactos; solo cambia
  la imagen de boot (el kernel).

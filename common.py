import yaml

__config = None

# Cargamos la config
def config():
	# Para usar la configuración que declaramos al inicio como None
	global __config
	# Si no estuvo cargada la vamos a cargar
	if not __config:
		# Abriendo en modo de lectura
		with open('config.yaml', mode='r') as f:
			__config = yaml.load(f)
	# Retornamos la configruación
	return __config

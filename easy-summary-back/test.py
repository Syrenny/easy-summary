import soundfile as sf

# Список доступных форматов
print("Supported formats:", "ogg" in str(sf.available_formats()).lower())

# Список поддерживаемых сабтипов
print("Supported subtypes:", "opus" in str(sf.available_subtypes()).lower())

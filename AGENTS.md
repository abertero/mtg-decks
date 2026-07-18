# Instrucciones para TTS - Asignación de Voces

## Reglas para asignación de voces en relatos

Cuando se solicite incorporar voces en archivos de relato (`tts/story/**/*.txt`):

### Identificación de personajes
1. Leer el archivo completo para identificar todos los personajes que hablan
2. Diferenciar entre:
   - **Relator/narrador**: Voz por defecto (sin tags)
   - **Personajes masculinos**: Usar voces masculinas (`alvaro`, `alex`, `tomas`, `jorge`, `lorenzo`)
   - **Personajes femeninos**: Usar voces femeninas (`elvira`, `dalia`, `catalina`, `elena`)

### Asignación de voces
- Cada personaje debe tener una voz consistente a lo largo del texto
- Personajes principales: asignar voces distintivas
- Personajes secundarios: pueden compartir voces si es necesario
- El relator NO lleva tags (usa la voz por defecto del archivo)

### Tags para situaciones especiales
- **Pensamientos internos**: Usar `{thought}` o combinar con voz del personaje `{alias+thought}`
- **Susurros**: Usar `{whisper}` o combinar con voz del personaje `{alias+whisper}`
- **Voz divina/poderosa**: Usar `{god}` o `{alias+god}`
- **Voz oscura/maligna**: Usar `{warlock}` o `{alias+warlock}`
- **Voz de criatura pequeña**: Usar `{goblin}` o `{alias+goblin}`

### Ejemplo de asignación
```
Personajes identificados:
- Sorin (vampiro, masculino) → {alvaro} para diálogo normal, {alvaro+whisper} para susurros, {alvaro+thought} para pensamientos
- Guerrero temur (humano, masculino) → {alex}
- Chamán Rushka (masculino) → {tomas}
- Capitán guerrero (masculino) → {alvaro} (puede coincidir con Sorin si es necesario)
```

### Notas importantes
- El usuario siempre especificará en qué archivo trabajar
- Pedir confirmación si hay ambigüedad sobre el género de un personaje
- Mantener consistencia: mismo personaje = misma voz en todo el texto
- Los tags deben estar balanceados (cada apertura tiene su cierre)

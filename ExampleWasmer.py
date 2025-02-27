from wasmer import engine, Store, Module, Instance

# Crear un almacén (Store)
store = Store()

# Definir un módulo WebAssembly en formato WAT
wasm_code = """
(module
  (type (func (param i32 i32) (result i32)))
  (func (export "sum") (type 0) (param i32 i32) (result i32)
    local.get 0
    local.get 1
    i32.add))
"""

# Compilar el módulo
module = Module(store, wasm_code)

# Instanciar el módulo
instance = Instance(module)

# Obtener la función exportada "sum"
sum_function = instance.exports.sum

# Llamar a la función con argumentos
result = sum_function(5, 37)
print(result)  # Debería imprimir 42

# AgriCorp: sistema distribuido con gRPC para una red de acopio agrícola

## Caso de estudio

Desarrollé un sistema distribuido para una red de acopio agrícola enfocada en el monitoreo y la gestión de productos como café y cacao en regiones de alta producción. El sistema resuelve la ineficiencia de las arquitecturas REST tradicionales basadas en texto (JSON sobre HTTP/1.1) usando gRPC y Protocol Buffers sobre HTTP/2, con serialización binaria compacta y soporte nativo para streaming de datos.

Despliegue: https://agricorp-grpc.onrender.com

## Cómo implementé gRPC

**Contrato como única fuente de verdad.** Diseñé la API a partir del archivo `protos/agricultural/v1/agricultural_market.proto`, no escribiendo controladores HTTP. Ahí están definidos los servicios, los mensajes y los tipos. El código de servidores y clientes se genera desde ese archivo con `grpc_tools.protoc`, así que ambos lados comparten exactamente los mismos tipos de punta a punta.

**Dos microservicios independientes.** Cada uno corre en su propio proceso, con su propio puerto y su propio health check (`grpc.health.v1`):

- **Pricing Microservice (puerto 50051):** atiende llamadas unarias. `ListProducts` entrega el catálogo y `GetProductPrice` devuelve el precio actual, el precio anterior, la variación porcentual y la tendencia del producto.
- **Telemetry Microservice (puerto 50052):** atiende client streaming. Con `StreamTelemetry`, una estación IoT abre un solo stream, envía miles de lecturas de temperatura, humedad y peso, y al cerrarlo recibe un resumen con promedios, rangos, peso total y alertas de almacenamiento.

**Sin verbos HTTP.** El backend no tiene `GET` ni `POST`; toda la comunicación son métodos RPC tipados sobre HTTP/2.

**Programación orientada a objetos.** El backend y los clientes están organizados en clases con una sola responsabilidad: repositorio de precios, simulador de mercado, política de almacenamiento, validador, agregador de telemetría, servicers y proxys de cliente. Las dependencias se inyectan por constructor.

**Manejo de errores gRPC.** Uso `NOT_FOUND` para productos inexistentes, `INVALID_ARGUMENT` para lecturas fuera de rango y `UNAVAILABLE` cuando un servicio no responde.

**Dashboard.** Lo hice en Streamlit y se conecta a los dos microservicios por canales gRPC. Muestra el estado de cada servicio, los resultados de cada llamada y la diferencia de tamaño entre el mensaje en Protobuf y el mismo mensaje en JSON.

## Cómo ejecutarlo

Requisitos: Python 3.12 o superior y Git.

```bash
git clone https://github.com/solartedaniers/AgriCorp-gRPC-.git
cd AgriCorp-gRPC-

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux o macOS

pip install -r requirements.txt
python tools/generate_contracts.py
python launcher.py
```

Luego abro `http://localhost:8501`. El launcher arranca el Pricing y el Telemetry como procesos separados, espera a que ambos estén disponibles y después inicia el dashboard.

Para correr las pruebas:

```bash
python -m pytest -q
```

Con Docker:

```bash
docker compose up --build
```

## Autor

Daniers Alexander Solarte Lima
# Auth Utils

JWT authentication utilities for microservices.

## Installation

```bash
poetry add git+https://your-repository-url/auth_utils.git
```

## Usage

```python
from auth_utils.check_auth import auth_dep

# Use auth_dep as FastAPI dependency for protected endpoints
@app.get("/protected", dependencies=[Depends(auth_dep)])
async def protected_route():
    return {"message": "This is protected"}
```

Make sure to place your `public.pem` file in the root directory of your service.

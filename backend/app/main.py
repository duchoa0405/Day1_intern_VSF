import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.api.v1 import health, products, purchase_orders, orders, analytics

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Hệ thống Backend API quản lý Doanh thu, Landed Cost và Lợi nhuận Ròng cho Shop Quần Áo Online.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các API Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health Check"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/catalog", tags=["Catalog & SKU Variants"])
app.include_router(purchase_orders.router, prefix=f"{settings.API_V1_STR}/purchase-orders", tags=["Inbound & Landed Cost Engine"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["Order Settlement & Net Profit Engine"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Financial Reports & P&L Analytics"])

# Đường dẫn thư mục giao diện frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/style.css", include_in_schema=False)
def serve_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"))

@app.get("/app.js", include_in_schema=False)
def serve_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "app.js"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

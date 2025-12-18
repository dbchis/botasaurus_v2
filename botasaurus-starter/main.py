# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import List, Union, Optional
from src.scrape_heading_task import scrape_places_quick
import traceback
import httpx

app = FastAPI(title="Crawl API",
              description="Crawl dữ liệu Google Maps", version="1.0")


# --- Model dữ liệu ---
class CrawlRequest(BaseModel):
    query: Union[str, List[str]]                # Cho phép 1 hoặc nhiều query
    # ✅ Thêm callback_url để backend gửi về
    callback_url: Optional[str] = None


# --- Hàm xử lý crawl ---
def crawlRequest(queries: Union[str, List[str]]):
    """Thực hiện crawl cho từng query, trả về danh sách kết quả"""
    if isinstance(queries, str):
        queries = [queries]

    all_results = []

    for query in queries:
        print(f"\n[INFO] Đang xử lý: {query}")
        try:
            place_data = scrape_places_quick(query)
            all_results.append({
                "query": query,
                "total": len(place_data),
                "data": place_data
            })
        except Exception as e:
            print(f"[ERROR] Lỗi khi crawl '{query}': {e}")
            traceback.print_exc()
            all_results.append({
                "query": query,
                "total": 0,
                "error": str(e),
                "data": []
            })

    return all_results


# --- Background crawl ---
def crawl_and_callback(queries: Union[str, List[str]], callback_url: str):
    """Chạy crawl ở background và gọi callback về backend khi xong"""
    try:
        print(f"[BACKGROUND] Start crawling for: {queries}")
        results = crawlRequest(queries)
        total_queries = len(results)
        total_places = sum(r.get("total", 0) for r in results)
        payload = {
            "status": "success",
            "total_queries": total_queries,
            "total_places": total_places,
            "results": results
        }

        if callback_url:
            print(f"[CALLBACK] Sending results to {callback_url}")
            with httpx.Client(timeout=60) as client:
                response = client.post(callback_url, json=payload)
                print(
                    f"[CALLBACK RESPONSE] {response.status_code} - {response.text}")

    except Exception as e:
        print("❌ Error in crawl_and_callback:", e)
        traceback.print_exc()


# --- API chính ---
@app.post("/crawl")
async def crawl_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Nhận payload JSON từ backend:
      {
        "query": [...],
        "callback_url": "http://localhost:8000/api/crawl_callback?job_id=..."
      }
    """
    try:
        data = await request.json()
        payload = CrawlRequest(**data)  # ✅ parse đúng kiểu có callback_url

        if payload.callback_url:
            # Chạy crawl nền -> trả ngay cho backend, không timeout
            background_tasks.add_task(
                crawl_and_callback, payload.query, payload.callback_url)
            print(f"[INFO] Crawl started (callback: {payload.callback_url})")
            return {"status": "started", "msg": "Crawling in background, will callback when done."}

        # Nếu không có callback (chạy trực tiếp)
        results = crawlRequest(payload.query)
        return {"status": "success", "results": results}

    except Exception as e:
        print("❌ Error in crawl_endpoint:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
# jksadkfjksfj

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

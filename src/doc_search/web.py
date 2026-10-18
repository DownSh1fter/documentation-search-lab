"""Small browser interface for the documentation search baseline."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from doc_search.data import load_passages
from doc_search.retrieval import TfidfRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="Documentation Search Lab")
retriever = TfidfRetriever(load_passages(PROJECT_ROOT / "data" / "corpus.jsonl"))


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Поиск по документации Python</title>
  <style>
    :root{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#e8edf5;background:#10151d}
    *{box-sizing:border-box}body{margin:0}main{max-width:900px;margin:56px auto;padding:0 22px}
    h1{font-size:clamp(28px,5vw,42px);margin:0 0 10px}p{color:#a9b5c7;line-height:1.6}
    form{display:flex;gap:10px;margin:28px 0 12px}input,select,button{font:inherit;border-radius:10px;padding:13px 15px}
    input{flex:1;min-width:0;background:#1b2431;border:1px solid #344155;color:#fff}
    select{background:#1b2431;color:#fff;border:1px solid #344155}button{border:0;background:#73a7ff;color:#09111e;font-weight:700;cursor:pointer}
    button:disabled{opacity:.6;cursor:wait}.hint,#status{font-size:14px;color:#91a0b5}.result{background:#18212d;border:1px solid #2c394a;border-radius:14px;padding:20px;margin:14px 0}
    .meta{display:flex;justify-content:space-between;gap:12px;color:#9eacc0;font-size:13px}.result h2{font-size:18px;margin:12px 0}
    .result p{color:#d1d9e5;margin:0 0 14px;white-space:pre-wrap}.result a{color:#8db8ff;text-decoration:none}
    .bar{height:5px;background:#293545;border-radius:5px;margin:10px 0 14px;overflow:hidden}.bar span{display:block;height:100%;background:#73a7ff}
    @media(max-width:600px){form{flex-wrap:wrap}input{flex-basis:100%}select{flex:1}}
  </style>
</head>
<body><main>
  <h1>Поиск по документации Python</h1>
  <p>Введите вопрос на английском и получите подходящие фрагменты документации. Сейчас используется TF-IDF — поиск по совпадению слов.</p>
  <form id="search-form"><input id="query" placeholder="Например: How do I read a text file?" required maxlength="500">
    <select id="top-k" aria-label="Количество результатов"><option value="3">3 результата</option><option value="5" selected>5 результатов</option><option value="10">10 результатов</option></select>
    <button id="submit" type="submit">Найти</button></form>
  <div class="hint">Совет: попробуйте запросы про файлы, исключения или списки.</div><div id="status" role="status"></div><section id="results"></section>
</main>
<script>
const form=document.querySelector('#search-form'),button=document.querySelector('#submit'),status=document.querySelector('#status'),results=document.querySelector('#results');
form.addEventListener('submit',async event=>{event.preventDefault();button.disabled=true;status.textContent='Ищем…';results.replaceChildren();
  try{const response=await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:document.querySelector('#query').value,top_k:Number(document.querySelector('#top-k').value)})});
    const data=await response.json();if(!response.ok)throw new Error(data.detail||'Не удалось выполнить поиск');
    if(!data.results.length){status.textContent='Подходящих фрагментов не найдено. Попробуйте переформулировать вопрос.';return}
    status.textContent=`Найдено фрагментов: ${data.results.length}`;
    for(const [index,item] of data.results.entries()){const card=document.createElement('article');card.className='result';
      const meta=document.createElement('div');meta.className='meta';meta.textContent=`Результат ${index+1} · TF-IDF ${item.score.toFixed(3)}`;
      const title=document.createElement('h2');title.textContent=item.title;const bar=document.createElement('div');bar.className='bar';const fill=document.createElement('span');fill.style.width=`${Math.min(item.score*100,100)}%`;bar.append(fill);
      const text=document.createElement('p');text.textContent=item.text;const link=document.createElement('a');link.href=item.source_url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='Открыть источник ↗';
      card.append(meta,title,bar,text,link);results.append(card)}
  }catch(error){status.textContent=error.message}finally{button.disabled=false}});
</script></body></html>"""


@app.post("/api/search")
def search(request: SearchRequest) -> dict[str, list[dict[str, str | float]]]:
    if not request.query.strip():
        raise HTTPException(status_code=422, detail="Введите поисковый запрос")
    matches = retriever.search(request.query, top_k=request.top_k)
    return {
        "results": [
            {
                "title": match.passage.title,
                "text": match.passage.text,
                "source_url": match.passage.source_url,
                "score": match.score,
            }
            for match in matches
        ]
    }


def main() -> None:
    import uvicorn

    uvicorn.run("doc_search.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()

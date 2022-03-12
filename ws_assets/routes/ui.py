from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def ui():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Demo</title>
        </head>
        <body>
            <h1>WebSocket Demo</h1>
            
            <span style="font-family: 'Courier New', monospace;">{"action": "assets", "message": {}}<span/>
            <br/>
            <span style="font-family: 'Courier New', monospace;">{"action": "subscribe", "message": {"assetId": 1}}<span/>
            <br/>
            <br/>
            
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                let socket = new WebSocket(`ws://localhost:8080/api/v1/websocket`);
                
                socket.onopen = function(e) {
                    console.log("[open] Websocket connection opened.");
                    console.log(e);
                };
                
                socket.onclose = function(e) {
                    if (e.wasClean) {
                        console.log("[close] Websocket connection closed.");
                    } else {
                        console.log("[close] Websocket connection interrupted.");
                    }
                    console.log(e);
                };
                
                socket.onerror = function(e) {
                    console.log("[error] Websocket error.");
                    console.log(e);
                };
                
                socket.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    socket.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """

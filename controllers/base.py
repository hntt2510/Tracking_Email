from typing import Tuple, Any, Callable
from flask import render_template_string, request

def redirect_auto_close(status: bool, message: str, close_time: int = 5):
  status_str = "Success" if status else "Failure"
  status_color = "#28a745" if status else "#dc3545"
  html_content = f"""
  <!DOCTYPE html>
  <html>
  <head>
    <title>Email Tracking</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        background-color: #f8f9fa;
        color: #343a40;
        text-align: center;
        padding-top: 100px;
      }}
      .header {{
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 30px;
        color: #007bff;
      }}
      .status {{
        font-size: 28px;
        font-weight: bold;
        color: {status_color};
      }}
      .message {{
        font-size: 22px;
        margin-top: 20px;
      }}
      .countdown {{
        font-size: 18px;
        margin-top: 40px;
        color: #6c757d;
      }}
    </style>
    <script type="text/javascript">
      let countdown = {close_time};
      function updateCountdown() {{
        document.getElementById('countdown').textContent = countdown;
        if (countdown === 0) {{
          window.open('', '_self', '');
          window.close();
        }}
        countdown--;
      }}
      window.onload = function() {{
        updateCountdown();
        setInterval(updateCountdown, 1000);
      }};
    </script>
  </head>
  <body>
    <div class="header">Response from Email Tracking System</div>
    <div class="status">Status: {status_str}</div>
    <div class="message">{message}</div>
    <div class="countdown">
      This page will close automatically after <span id="countdown">{close_time}</span> seconds.
    </div>
  </body>
  </html>
  """
  return render_template_string(html_content)

def try_get_param(param_name: str, as_type: Callable = str) -> Tuple[bool, Any]:
  value = request.args.get(param_name, None)
  if value is None:
    return False, None
  
  try:
    return True, as_type(value)
  except (ValueError, TypeError):
    return False, None
import datetime
from tkinter import simpledialog
import database
from typing import Optional, Any

class SessionManager:
    def __init__(self, app: Any):
        self.app = app
        self.current_session: Optional[int] = None

    def init_daily_session(self) -> None:
        session = database.get_active_session()
        today_str = datetime.date.today().isoformat()
        
        if session:
            start_time = session['start_time'] 
            if start_time.startswith(today_str):
                self.current_session = session['id']
                return
            else:
                database.close_session(session['id'], 0) 
        
        self.app.after(100, self.ask_initial_cash)

    def ask_initial_cash(self) -> None:
        initial = simpledialog.askfloat("Inicio de Turno", "Ingrese efectivo inicial en caja:", parent=self.app)
        if initial is None: initial = 0.0
        self.current_session = database.create_session(initial)
        
        if hasattr(self.app, 'left_panel'):
            self.app.left_panel.focus_entry()

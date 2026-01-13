import os
import json
import datetime
import traceback
from fpdf import FPDF

from kivy.utils import platform 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

# --- CONFIGURACIÓN DE RUTA INTERNA (REGLA ANDROID 15) ---
def get_paths():
    if platform == 'android':
        path = App.get_running_app().user_data_dir
    else:
        path = "YOURMOBILE_CAJA"
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return {
        "base": path,
        "staff": os.path.join(path, "staff_list.txt"),
        "temp": os.path.join(path, "daily_temp_cache.json"),
        "log": os.path.join(path, "ERROR_LOG.txt")
    }

# --- PDF PROFESIONAL ---
class ReportePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 70, 140)
        self.cell(0, 10, 'YOUR MOBILE STORE - DAILY FINANCIAL REPORT', 0, 1, 'C')
        self.ln(5)

# --- PANTALLA PRINCIPAL ---
class MenuPrincipal(Screen):
    def on_pre_enter(self):
        self.lbl_info.text = f"Records: {len(App.get_running_app().products)}"

    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        layout.add_widget(Label(text="YOUR MOBILE STORE", font_size='22sp', bold=True, size_hint_y=None, height=dp(50), color=(0.1, 0.4, 0.7, 1)))
        
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        container.bind(minimum_height=container.setter('height'))

        # RECTIFICACIÓN: TODAS LAS OPCIONES DEL MENÚ
        menu_items = [
            ("--- INCOMES ---", [
                ("NEW SALE", "PRODUCT"), 
                ("REPAIR / SERVICE", "SERVICE")
            ]),
            ("--- INVESTMENTS ---", [
                ("INVESTMENT SAN JUAN", "INV_SJ"), 
                ("INVESTMENT TOBAGO", "INV_TB"), 
                ("INVESTMENT ARANGUEZ", "INV_AR")
            ]),
            ("--- OTHER OUTFLOWS ---", [
                ("OWNER'S SON", "SON"), 
                ("VOUCHER", "VOUCHER"), 
                ("RENT PAYMENT", "RENT"), 
                ("WAGES / SALARIES", "WAGES")
            ]),
        ]

        for title, items in menu_items:
            container.add_widget(Label(text=title, size_hint_y=None, height=dp(35), color=(0.4, 0.4, 0.4, 1), bold=True))
            for text, cat in items:
                b = Button(text=text, size_hint_y=None, height=dp(50), background_color=(0.15, 0.5, 0.35, 1))
                b.bind(on_release=lambda x, c=cat: self.go_input(c))
                container.add_widget(b)

        btn_staff = Button(text="[ 10 ] STAFF MANAGEMENT", size_hint_y=None, height=dp(55), background_color=(0.1, 0.4, 0.6, 1), bold=True)
        btn_staff.bind(on_release=lambda x: setattr(self.manager, 'current', 'staff'))
        container.add_widget(btn_staff)

        scroll.add_widget(container)
        layout.add_widget(scroll)
        
        btn_save = Button(text="SAVE & SHARE REPORT", size_hint_y=None, height=dp(60), background_color=(0.1, 0.6, 0.2, 1), bold=True)
        btn_save.bind(on_press=lambda x: App.get_running_app().generate_report())
        layout.add_widget(btn_save)

        self.lbl_info = Label(text="Records: 0", size_hint_y=None, height=dp(25), font_size='11sp')
        layout.add_widget(self.lbl_info)
        self.add_widget(layout)

    def go_input(self, cat):
        self.manager.get_screen('input').category = cat
        self.manager.current = 'input'

# --- PANTALLA DE ENTRADA (LÓGICA DE SUBDIRECTORIOS RECTIFICADA) ---
class InputScreen(Screen):
    category = ""; fields = {}
    def on_pre_enter(self):
        self.container.clear_widgets(); self.fields = {}
        self.title.text = f"CATEGORY: {self.category}"
        
        # DEFINICIÓN DE CAMPOS SEGÚN LA OPCIÓN ELEGIDA
        if self.category == "WAGES":
            self.add_f('worker', "Worker Name:"); self.add_f('amt', "Amount Paid:")
        elif self.category in ["INV_SJ", "INV_TB", "INV_AR"]:
            self.add_f('amt', "Investment Amount:"); self.add_f('taxi', "Taxi Cost:")
        elif self.category == "RENT":
            self.add_f('ar', "Aranguez Rent:"); self.add_f('sj', "San Juan Rent:"); self.add_f('hm', "Home Rent:")
        elif self.category in ["SON", "VOUCHER"]:
            self.add_f('amt', "Amount:")
        else: # PRODUCT O SERVICE
            self.add_f('name', "Item/Service Name:"); self.add_f('qty', "Quantity:")
            self.add_f('price', "Sale Price (Total):"); self.add_f('cost', "Cost (Total):")
            self.add_f('taxi', "Taxi/Fee:")

    def add_f(self, key, label):
        self.container.add_widget(Label(text=label, size_hint_y=None, height=dp(20)))
        ti = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        self.fields[key] = ti; self.container.add_widget(ti)

    def save_record(self, _):
        app = App.get_running_app(); f = self.fields
        def v(k):
            try: return float(f[k].text) if f[k].text else 0.0
            except: return 0.0

        # RECTIFICACIÓN DE CÁLCULOS POR CATEGORÍA
        res = {"desc": "", "qty": 1, "sale": 0.0, "cost": 0.0, "taxi": 0.0, "net": 0.0}
        
        if self.category == "WAGES":
            amt = v('amt')
            res.update({"desc": f"WAGE: {f['worker'].text.upper()}", "cost": amt, "net": -amt})
        elif "INV_" in self.category:
            amt, taxi = v('amt'), v('taxi')
            res.update({"desc": self.category.replace("_", " "), "cost": amt, "taxi": taxi, "net": -(amt + taxi)})
        elif self.category == "RENT":
            for k, n in [('ar', "RENT ARANGUEZ"), ('sj', "RENT SAN JUAN"), ('hm', "RENT HOME")]:
                val = v(k)
                if val > 0: app.products.append({"desc": n, "qty": 1, "sale": 0, "cost": val, "taxi": 0, "net": -val})
            app.save_temp(); self.manager.current = 'menu'; return
        elif self.category in ["SON", "VOUCHER"]:
            amt = v('amt')
            res.update({"desc": f"OUTFLOW: {self.category}", "cost": amt, "net": -amt})
        else:
            name = f['name'].text.upper() or "ITEM"
            q, p, c, t = int(v('qty') or 1), v('price'), v('cost'), v('taxi')
            res.update({"desc": name, "qty": q, "sale": p, "cost": c, "taxi": t, "net": (p - c - t)})

        app.products.append(res); app.save_temp(); self.manager.current = 'menu'

    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        self.title = Label(text="", bold=True, size_hint_y=None, height=dp(40))
        l.add_widget(self.title)
        self.container = BoxLayout(orientation='vertical', spacing=dp(5))
        l.add_widget(self.container)
        btn = Button(text="SAVE RECORD", size_hint_y=None, height=dp(55), background_color=(0.1, 0.5, 0.8, 1))
        btn.bind(on_press=self.save_record); l.add_widget(btn)
        self.add_widget(l)

# --- GESTIÓN DE STAFF ---
class StaffScreen(Screen):
    def on_pre_enter(self): self.load()
    def __init__(self, **kw):
        super().__init__(**kw)
        l = BoxLayout(orientation='vertical', padding=dp(20))
        l.add_widget(Label(text="STAFF MANAGEMENT", bold=True, size_hint_y=None, height=40))
        self.inp = TextInput(hint_text="New Name", multiline=False, size_hint_y=None, height=45)
        l.add_widget(self.inp)
        btn = Button(text="ADD", size_hint_y=None, height=45); btn.bind(on_press=self.add); l.add_widget(btn)
        self.scroll = ScrollView(); self.box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.box.bind(minimum_height=self.box.setter('height')); self.scroll.add_widget(self.box); l.add_widget(self.scroll)
        back = Button(text="BACK", size_hint_y=None, height=50); back.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu')); l.add_widget(back)
        self.add_widget(l)

    def load(self):
        self.box.clear_widgets(); p = get_paths()
        if os.path.exists(p["staff"]):
            with open(p["staff"], "r") as f:
                for line in f:
                    n = line.strip()
                    if n:
                        row = BoxLayout(size_hint_y=None, height=40)
                        row.add_widget(Label(text=n))
                        self.box.add_widget(row)

    def add(self, _):
        if self.inp.text:
            with open(get_paths()["staff"], "a") as f: f.write(self.inp.text.upper() + "\n")
            self.inp.text = ""; self.load()

# --- APP PRINCIPAL ---
class MobileStoreApp(App):
    products = []
    def build(self):
        self.paths = get_paths(); self.load_temp()
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuPrincipal(name='menu')); sm.add_widget(InputScreen(name='input')); sm.add_widget(StaffScreen(name='staff'))
        return sm

    def load_temp(self):
        if os.path.exists(self.paths["temp"]):
            try:
                with open(self.paths["temp"], "r") as f: self.products = json.load(f)
            except: self.products = []

    def save_temp(self):
        with open(self.paths["temp"], "w") as f: json.dump(self.products, f)

    def generate_report(self):
        if not self.products: return
        try:
            pdf = ReportePDF(); pdf.add_page(); now = datetime.datetime.now()
            pdf.set_font('Arial', 'B', 9)
            # Encabezados de tabla
            header = [('DESC', 65), ('QTY', 12), ('SALE', 25), ('COST', 25), ('TAXI', 25), ('NET', 28)]
            for t, w in header: pdf.cell(w, 10, t, 1, 0, 'C')
            pdf.ln()
            
            pdf.set_font('Arial', '', 8); total = 0
            for p in self.products:
                pdf.cell(65, 8, p['desc'][:35], 1)
                pdf.cell(12, 8, str(p['qty']), 1, 0, 'C')
                pdf.cell(25, 8, f"{p['sale']:.2f}", 1, 0, 'R')
                pdf.cell(25, 8, f"{p['cost']:.2f}", 1, 0, 'R')
                pdf.cell(25, 8, f"{p['taxi']:.2f}", 1, 0, 'R')
                pdf.cell(28, 8, f"{p['net']:.2f}", 1, 0, 'R')
                pdf.ln(); total += p['net']

            pdf.ln(5); pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"TOTAL PROFIT: {total:.2f}", 0, 1, 'R')
            
            f_name = f"REPORT_{now.strftime('%Y%m%d_%H%M')}.pdf"
            full_path = os.path.join(self.paths["base"], f_name)
            pdf.output(full_path)
            self.share(full_path)
            if os.path.exists(self.paths["temp"]): os.remove(self.paths["temp"])
        except:
            with open(self.paths["log"], "w") as f: f.write(traceback.format_exc())

    def share(self, path):
        if platform == 'android':
            from jnius import autoclass, cast
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = autoclass('android.content.Intent')(autoclass('android.content.Intent').ACTION_SEND)
            intent.setType("application/pdf")
            uri = autoclass('androidx.core.content.FileProvider').getUriForFile(activity, "com.yourmobile.store.fileprovider", autoclass('java.io.File')(path))
            intent.putExtra(autoclass('android.content.Intent').EXTRA_STREAM, uri)
            intent.addFlags(autoclass('android.content.Intent').ACTION_GRANT_READ_URI_PERMISSION)
            activity.startActivity(autoclass('android.content.Intent').createChooser(intent, cast(autoclass('java.lang.String'), "Share Report")))

if __name__ == '__main__':
    MobileStoreApp().run()
        

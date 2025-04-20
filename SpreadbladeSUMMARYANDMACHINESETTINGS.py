import tkinter as tk
from tkinter import ttk, messagebox
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import sys # Hata ayıklama için eklendi, isterseniz kaldırılabilir

# --- Güvenli Matematiksel İşlem Fonksiyonları ---
def safe_acos(value):
    """arccos için alan hatasını önler, değeri [-1, 1] aralığına sıkıştırır."""
    return math.acos(max(-1.0, min(1.0, value)))

def safe_asin(value):
    """arcsin için alan hatasını önler, değeri [-1, 1] aralığına sıkıştırır."""
    return math.asin(max(-1.0, min(1.0, value)))

def safe_sqrt(value):
    """sqrt için alan hatasını önler, negatif girdiler için 0 döndürür."""
    return math.sqrt(max(0.0, value))

def safe_log10(value):
    """log10 için alan hatasını önler, <= 0 girdiler için çok küçük pozitif sayı kullanır."""
    return math.log10(max(1e-10, value))

def safe_division(numerator, denominator, default=float('inf')):
    """Sıfıra bölme hatasını önler."""
    if abs(denominator) < 1e-10:
        # print(f"Uyarı: Sıfıra bölme denemesi ({numerator}/{denominator}). Varsayılan değer ({default}) döndürülüyor.")
        return default
    return numerator / denominator
# --- ---

class SpiralBevelCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gleason SB Hesaplayıcı (SD3033C)")
        # Daha büyük bir başlangıç boyutu
        self.root.geometry("900x700")

        # Ana çerçeve
        main_frame = ttk.Frame(root, padding="5")
        main_frame.pack(fill="both", expand=True)

        # Sekmeler için Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Her sekme için çerçeveler
        self.input_frame = ttk.Frame(self.notebook, padding="10")
        self.sb1_frame = ttk.Frame(self.notebook, padding="5")
        self.sb2_frame = ttk.Frame(self.notebook, padding="5")
        self.sb3_frame = ttk.Frame(self.notebook, padding="5")
        self.graph_frame = ttk.Frame(self.notebook, padding="5")

        # Çerçeveleri Notebook'a ekle
        self.notebook.add(self.input_frame, text="Giriş Parametreleri")
        self.notebook.add(self.sb1_frame, text="SB1 (Nokta Genişlikleri)")
        self.notebook.add(self.sb2_frame, text="SB2 (Kesici Özellikleri)")
        self.notebook.add(self.sb3_frame, text="SB3 (Kalınlıklar & Ayarlar)")
        self.notebook.add(self.graph_frame, text="Grafikler")

        # Hesaplanan değerleri saklamak için sözlük
        self.values = {}
        # Sonuç etiketlerini saklamak için sözlükler (Öğe numarasına göre)
        self.result_labels = {} # Tüm labelları tek bir yerde toplayalım

        # Arayüz bileşenlerini oluştur
        self.setup_input_frame()
        self.setup_sb1_frame()
        self.setup_sb2_frame()
        self.setup_sb3_frame()
        self.setup_graph_frame()


    def setup_input_frame(self):
        """Giriş parametreleri sekmesini oluşturur."""
        params_frame = ttk.LabelFrame(self.input_frame, text="Dişli Parametreleri", padding="10")
        params_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Parametre tanımları: (Etiket, değişken adı, varsayılan değer, birim)
        # Dokümandaki referanslara göre isimlendirme
        parameters = [
            ("Pinyon Diş Sayısı (n)", "n", 20, ""),
            ("Dişli Diş Sayısı (N)", "N", 40, ""),
            ("Diametral Pitch (Pd)", "Pd", 5, "1/inç"),
            ("Basınç Açısı (°)", "phi_deg", 20, "°"),
            ("Mil Açısı (°)", "shaft_angle_deg", 90, "°"),
            ("Ort. Spiral Açısı (°)", "psi_deg", 35, "°"),
            ("Yüz Genişliği (F)", "F", 1.5, "inç"),
            ("Kesici Yarıçapı (rc)", "rc", 3.5, "inç"),
            ("Pinyon Addendum (a₀P)", "a0P", 0.170, "inç"), # Örnek değerler güncellendi
            ("Dişli Addendum (a₀G)", "a0G", 0.230, "inç"), # Örnek değerler güncellendi
            ("Pinyon Dedendum (b₀P)", "b0P", 0.269, "inç"), # Örnek değerler güncellendi
            ("Dişli Dedendum (b₀G)", "b0G", 0.209, "inç"), # Örnek değerler güncellendi
            ("Pinyon Dış Kalınlık (t₀PL)", "t0PL", 0.250, "inç"), # Yaklaşık, hesaplanmalı normalde
            ("Dişli Dış Kalınlık (t₀G)", "t0G", 0.364, "inç"),   # Yaklaşık, hesaplanmalı normalde
        ]

        self.input_vars = {}
        # Girdi alanlarını daha düzenli yerleştirelim
        row_num = 0
        col_num = 0
        for i, (label, var_name, default, unit) in enumerate(parameters):
            ttk.Label(params_frame, text=f"{label}:").grid(row=row_num, column=col_num, padx=5, pady=3, sticky="w")
            var = tk.StringVar(value=str(default))
            self.input_vars[var_name] = var
            entry = ttk.Entry(params_frame, textvariable=var, width=10)
            entry.grid(row=row_num, column=col_num + 1, padx=5, pady=3, sticky="w")
            ttk.Label(params_frame, text=unit).grid(row=row_num, column=col_num + 2, padx=5, pady=3, sticky="w")

            # İki sütunlu yerleşim için
            col_num += 3
            if col_num >= 6:
                col_num = 0
                row_num += 1


        # Butonlar
        button_frame = ttk.Frame(self.input_frame, padding="10")
        button_frame.grid(row=1, column=0, pady=10, sticky="ew")

        calc_button = ttk.Button(button_frame, text="Hesapla", command=self.calculate_all, padding=10)
        calc_button.pack(side="left", padx=10, expand=True, fill="x")

        # Yardım butonu şimdilik kaldırıldı, istenirse eklenebilir
        # help_button = ttk.Button(button_frame, text="Yardım", command=self.show_help, padding=10)
        # help_button.pack(side="right", padx=10, expand=True, fill="x")

        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.rowconfigure(0, weight=1)

    def setup_calculation_frame(self, parent_frame, title, items):
        """SB1, SB2, SB3 sekmeleri için genel sonuç çerçevesi oluşturucu."""
        canvas = tk.Canvas(parent_frame)
        scrollbar_y = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas, padding="5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Yerleşim
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)


        ttk.Label(scrollable_frame, text=title, font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=5, padx=5, pady=10, sticky="w") # 5 sütun

        # Başlıklar
        headers = ["Öğe", "Formül/Sembol", "Açıklama", "Pinyon (L)", "Dişli (R)"]
        for j, header in enumerate(headers):
             ttk.Label(scrollable_frame, text=header, font=("Arial", 10, "bold")).grid(row=1, column=j, padx=5, pady=3, sticky="w")

        # Ayırıcı
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=2, column=0, columnspan=5, sticky='ew', pady=5)

        # Öğeleri ekle
        for i, item_data in enumerate(items):
            row_num = i + 3
            item_num_str = item_data[0]
            formula_symbol = item_data[1]
            description = item_data[2]

            ttk.Label(scrollable_frame, text=item_num_str).grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(scrollable_frame, text=formula_symbol).grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
            ttk.Label(scrollable_frame, text=description).grid(row=row_num, column=2, padx=5, pady=2, sticky="w")

            # Pinyon (L) ve Dişli (R) sütunları için labelları oluştur ve sakla
            for j, suffix in enumerate(["L", "R"]):
                 key = f"{item_num_str}{suffix}"
                 result_var = tk.StringVar(value="-")
                 self.result_labels[key] = result_var # Ana sözlükte sakla
                 label = ttk.Label(scrollable_frame, textvariable=result_var, width=15, anchor="e") # Sağa hizalı
                 label.grid(row=row_num, column=3 + j, padx=5, pady=2, sticky="ew")

        # Sütun genişliklerini ayarla
        scrollable_frame.columnconfigure(1, weight=1) # Formül
        scrollable_frame.columnconfigure(2, weight=2) # Açıklama
        scrollable_frame.columnconfigure(3, weight=1) # Pinyon
        scrollable_frame.columnconfigure(4, weight=1) # Dişli

    def get_sb1_items_from_pdf(self):
        # PDF Sayfa 16 ve metin açıklamalarına göre liste
        # ("Öğe No", "Formül/Sembol", "Açıklama") - 4. eleman (birim) kaldırıldı
        return [
            ("1", "n ; N", "Diş Sayısı (Pinyon ; Dişli)"),
            ("2", "Pd ; p", "Diametral Pitch ; Dairesel Pitch"),
            ("3", "d ; D", "Pitch Çapları"),
            ("4", "F ; F/2", "Yüz Genişliği ; Yarım Yüz Genişliği"),
            ("5", "A₀", "Dış Koni Mesafesi"),
            ("6", "A", "Ortalama Koni Mesafesi (Am)"),
            ("7", "Ai", "İç Koni Mesafesi"),
            ("8", "rc", "Kesici Yarıçapı"),
            ("9", "φ", "Normal Basınç Açısı"),
            ("10", "sin φ", "sin(Basınç Açısı)"),
            ("11", "cos φ", "cos(Basınç Açısı)"),
            ("12", "tan φ", "tan(Basınç Açısı)"),
            ("13", "ψ", "Ortalama Spiral Açısı"),
            ("14", "sin ψ", "sin(Spiral Açısı)"),
            ("15", "cos ψ", "cos(Spiral Açısı)"),
            ("16", "tan ψ", "tan(Spiral Açısı)"),
            ("17", "γ ; Γ", "Pitch Açıları (Pinyon ; Dişli)"),
            ("18", "sin γ ; sin Γ", "sin(Pitch Açıları)"),
            ("19", "cos γ ; cos Γ", "cos(Pitch Açıları)"),
            ("20", "tan γ ; tan Γ", "tan(Pitch Açıları)"),
            ("21", "a₀P ; a₀G", "Dış Addendumlar"),
            ("22", "b₀P ; b₀G", "Dış Dedendumlar"),
            ("23", "δp ; δG", "Dedendum Açıları"),
            ("24", "cos δp ; cos δG", "cos(Dedendum Açıları)"),
            ("25", "tan δp ; tan δG", "tan(Dedendum Açıları)"),
            ("26", "t₀PL ; t₀G", "Dış Çevresel Kalınlıklar"),
            ("27", "2(8)(14)-(6)", "Hesaplama: 2*rc*sin(ψ)-A0"),
            ("28", "(6)(27)/(5)+(5)", "Hesaplama: Öğe27+A0"), # Düzeltilmiş formül
            ("29", "(6)(27)/(7)+(7)", "Hesaplama: (A0*Öğe27)/Ai + Ai"), # Düzeltilmiş formül
            ("30", "sin Ψo = (28)/2(8)", "sin(Dış Spiral Açısı)"),
            ("31", "Ψo", "Dış Spiral Açısı"),
            ("32", "Ψo", "(PDF tekrarı? Ψi olmalı)"), # PDF'te 32 Ψo, 34 Ψi diyor
            ("33", "sin Ψi = (29)/2(8)", "sin(İç Spiral Açısı)"),
            ("34", "Ψi", "İç Spiral Açısı"),
            ("35", "cos Ψi", "cos(İç Spiral Açısı)"), # PDF'te 35 yok ama 46'da kullanılıyor
            ("36", "Bmin ; Bmax", "Min/Max Boşluk (Backlash)"),
            ("37", "b = (22)-(4)R(25)", "Ortalama Dedendum (b)"),
            ("38", "bi = (37)-(4)R(25)", "İç Dedendum (bi)"),
            ("39", "(22)L+(22)R", "Dış Dedendum Toplamı"), # PDF'te 39 = b0P+b0G
            ("40", "(38)L+(38)R", "İç Dedendum Toplamı"),
            ("41", "(6)(26)L / (5)", "Pinyon Dış Kalınlığı (t₀PL)"), # Düzeltilmiş formül
            ("42", "(7)(2)R / (5)", "Hesaplama: (Ai*p)/A0"), # Düzeltilmiş formül
            ("43", "WG'=(15)(41)-2(12)(37)R", "Teorik Dişli Nokta Genişliği"),
            ("44", "WG ; WRG", "Dişli Finiş; Kaba Nokta Genişliği"),
            ("45", "Wop=(2)R(32)-2(12)(39)-(44)L", "Pinyon Dış Limit Nokta Gen."), # Formül belirsiz
            ("46", "Wip=(42)(35)-2(12)(40)-(44)L", "Pinyon İç Limit Nokta Gen."),
            ("47", "WLP=min((45),(46))", "Pinyon Limit Nokta Genişliği"),
            ("48", "WRP=(47)-Stok Payı", "Pinyon Kaba Nokta Genişliği"),
        ]

    def get_sb2_items_from_pdf(self):
        # PDF Sayfa 17 ve metin açıklamalarına göre liste
        return [
            ("49", "WMP=max((45),(46))", "Maks Pinyon Yuva Genişliği"),
            ("50", "WB", "Bıçak Ucu Genişliği (Tablo/Formül)"),
            ("51", "(15)^2", "Hesaplama: cos(ψ)^2"), # Düzeltilmiş formül
            ("52", "1-(10)", "Hesaplama: 1-sin(φ)"),
            ("53", "(52)/(11)", "Hesaplama: Öğe52/cos(φ)"),
            ("54", "(7)(36)R/(5)", "Hesaplama: (Ai*Bmax)/A0"),
            ("55", "0.5(54)/(12)", "Hesaplama: 0.5*Öğe54/tan(φ)"),
            ("56", "c", "İç Boşluk (Clearance)"),
            ("57", "Ri=(7)(20)/(51)", "Hesaplama: (Ai*tan(Γ))/cos(ψ)^2"), # Pinyon için Sol Sütun
            ("58", "ai=(38)-(56)", "İç Addendum (bi-c)"), # (58a olarak belirtilmiş)
            ("59", "(1)/(19)", "Sanal Diş Sayısı Terimi (n/cosγ)"),
            ("60", "(59)L+(59)R", "Sanal Diş Sayısı Terimi Toplamı"),
            ("61", "Δa=(55)(59)/(60)", "Addendum Değişimi"),
            ("62", "(57)R ; (57)L", "Referans: Öğe 57 Değerleri"),
            ("63", "(61)R ; (61)L", "Referans: Öğe 61 Değerleri"),
            ("64", "a1=(58)+(63)", "Düzeltilmiş İç Addendum"),
            ("65", "R1=(62)-(63)", "Düzeltilmiş Ri"),
            ("66", "R1/a1=(65)/(64)", "Oran: R1/a1"),
            ("67", "K1", "Faktör (Grafik No. 1)"),
            ("68", "ro=(64)(67)", "Taban Kenar Yarıçapı"),
            ("69", "Δr=((56)-(55))/(52)", "Kenar Yarıçapı Artışı"),
            ("70", "r1=(68)+(69)", "Maks Yarıçap (Fillet)"),
            ("71", "r2=((50)-0.015)/(53)", "Maks Yarıçap (Taşlama)"),
            ("72", "(47)-(50)L", "Hesaplama: WLP - WB_Pinyon"),
            ("73", "(53)(72)+0.001", "Hesaplama: Öğe53*Öğe72+0.001"),
            ("74", "√(75)", "Hesaplama: sqrt(Öğe75)"), # Düzeltilmiş formül
            ("75", "(73)+0.002", "Hesaplama: Öğe73+0.002"),
            ("76", "(73)^2", "Hesaplama: Öğe73^2"), # Düzeltilmiş formül
            ("77", "r3=(0.063(74)+(75))/(76)", "Maks Yarıçap (Bozulma)"),
            ("78", "rE=min((70),(71),(77))", "Kesici Kenar Yarıçapı"),
            ("79", "#c'=(14)(23)/10.0", "Teorik Kesici No"),
            ("80", "#CR", "Kaba İşleme Kesici No"),
            ("81", "#CF", "Finiş Kesici No"),
            ("82", "ht", "Tam Diş Derinliği"),
            ("83", "(8)/(15)", "Hesaplama: rc/cos(ψ)"),
            ("84", "(6)-(8)(14)", "Hesaplama: A0-rc*sin(ψ)"),
            ("85", "(83)^2+(84)^2", "Hesaplama: Öğe83^2+Öğe84^2"),
            ("86", "√(85)", "Hesaplama: sqrt(Öğe85)"),
            ("87", "(38)L+(58)R ; (82)", "Derinlik Terimi ; Tam Derinlik"),
            ("88", "0.5(44)L+(12)(87)", "Hesaplama: 0.5*WG+tan(φ)*Öğe87"),
            ("89", "(8)±(88)", "Hesaplama: rc±Öğe88"),
            ("90", "(7) ; (5)", "Referans: Ai ; A0"),
            ("91", "(86)(89)/0.5", "Hesaplama: Öğe86*Öğe89/0.5"),
            ("92", "cosθ=((90)^2-(89)^2-(85))/(91)", "cos(Kesici Açısal Konum)"),
            ("93", "θ", "Kesici Açısal Konum"),
            ("94", "Δθ=(93)L-(93)R-1°", "Açı Farkı"),
            ("95", "Nb'=360°/(94)", "Maks Bıçak Sayısı"),
            ("96", "NB", "Gerçek Bıçak Sayısı (< Öğe 95)"),
        ]

    def get_sb3_items_from_pdf(self):
        # PDF Sayfa 18 ve metin açıklamalarına göre liste
        return [
            ("97", "((12)(22)R+(44)L)/0.5", "Hesaplama: (tan(φ)*b0G+WG)/0.5"),
            ("98", "(2)R(32)-(97)", "Hesaplama: p*Ψo-Öğe97"), # Formül belirsiz
            ("99", "((30)(97)±(30)(98))/2.0", "Hesaplama (Pinyon/Dişli)"), # +/- sırası önemli
            ("100", "ΔA", "Kalınlık Ölçüm Noktası Değişimi"),
            ("101", "max((99),(100))", "Maks(Öğe99, Öğe100)"),
            ("102", "(5)-(101)", "Hesaplama: A0-Öğe101"),
            ("103", "(101)(25)R", "Hesaplama: Öğe101*tan(δG)"),
            ("104", "(101)(25)M", "Hesaplama: Öğe101*tan(δp)"),
            ("105", "((22)R-(103))/0.5", "Hesaplama: (b0G-Öğe103)/0.5"),
            ("106", "((12)(105)+(44)L)/0.5", "Hesaplama: (tan(φ)*Öğe105+WG)/0.5"),
            ("107", "(97); (98)", "Referans: Öğe 97, 98"),
            ("108", "(21)-(104)", "Hesaplama: a0P-Öğe104"),
            ("109", "(6)(27)+(102)", "Hesaplama: A0*Öğe27+Öğe102"),
            ("110", "sinΦM=(109)/2(8)", "sin(Modifiye Basınç Açısı)"),
            ("111", "ΦM", "Modifiye Basınç Açısı"),
            ("112", "cosΦM", "cos(Modifiye Basınç Açısı)"),
            ("113", "(2)R(112)R", "Hesaplama: p*cos(ΦM)_Dişli"), # Formül belirsiz
            ("114", "(113)(102)R/(5)", "Hesaplama: Öğe113*Öğe102_Dişli/A0"),
            ("115", "tM=(106)L-(36)L;(114)-(106)R", "Ölçüm Kalınlığı (Min ; Max)"),
            ("116", "(112)^2/4.0", "Hesaplama: cos(ΦM)^2/4.0"),
            ("117", "(3)(102)/(5)", "Hesaplama: d*Öğe102/A0"),
            ("118", "(115)^2/(117)", "Hesaplama: tM^2/Öğe117"),
            ("119", "(19)(118)", "Hesaplama: cos(γ)*Öğe118"),
            ("120", "aM=(108)+(116)(119)", "Ölçüm Addendumu"),
            ("121", "F*Pd=(2)L(4)L", "Yüz Genişliği x Pitch"),
            ("122", "mF", "Yüzey Kavrama Oranı (Grafik 2)"),
            ("123", "XB=(5)(25)-(22)", "Kaydırma Tabanı (Pinyon)"),
            ("124", "V=(8)(15)", "Dikey Kesici Ayarı"),
            ("125", "H=(6)-(8)(14)", "Yatay Kesici Ayarı"),
            ("126", "ctn q=(125)/(124)", "cot(Kesici Açısal Konum q)"),
            ("127", "q", "Kesici Açısal Konum q"),
            ("128", "sin q", "sin(Kesici Açısal Konum q)"),
            ("129", "Ra=(24)/(18)", "Rulo Oranı (Pinyon)"),
            ("130", "(1)(129)/150.0", "Oran Dişlisi Ondalık Oran (150 d.)"),
            ("131", "m75=2(130)", "Ondalık Oran (Nc/75)"),
            ("132", "Nc/75", "Oran Dişlileri (Nc/75)"),
            ("133", "m50=3(130)", "Ondalık Oran (Nc/50)"),
            ("134", "Nc/50", "Oran Dişlileri (Nc/50)"),
            ("135", "", "Kızak-İş Parçası Test Rulosu"),
            ("136", "S=(124)/(128)", "Radyal Kesici Ayarı"),
            ("137", "Q=360°-(127)L.H.;(127)R.H.", "Kızak Açısı Ayarı"),
            ("138", "K2", "Makine Sabiti (Eksantrik)"),
            ("139", "sin(β/2)=(136)/(2(138))", "sin(Yarım Eksantrik Açı)"),
            ("140", "β/2", "Yarım Eksantrik Açı"),
            ("141", "β=2(140)", "Eksantrik Açı"),
            ("142", "Q=270°+(140)∓(127)", "Kızak Açısı (Alternatif Makine)"),
            ("143", "√( (138)^2-(136)^2 )", "Hesaplama: sqrt(K2^2-S^2)"),
            ("144", "Q=360°-(142)", "Kızak Açısı (Alternatif Makine)"),
        ]

    def setup_sb1_frame(self):
        self.setup_calculation_frame(self.sb1_frame, "SB1 (Nokta Genişlikleri)", self.get_sb1_items_from_pdf())

    def setup_sb2_frame(self):
        self.setup_calculation_frame(self.sb2_frame, "SB2 (Kesici Özellikleri)", self.get_sb2_items_from_pdf())

    def setup_sb3_frame(self):
        self.setup_calculation_frame(self.sb3_frame, "SB3 (Kalınlıklar & Ayarlar)", self.get_sb3_items_from_pdf())

    def setup_graph_frame(self):
        """Grafik sekmesini oluşturur."""
        graph_notebook = ttk.Notebook(self.graph_frame)
        graph_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.graph_frames = {}
        graph_info = [
            ("K1 Factor", "K1 Faktörü Grafiği", self.generate_k1_graph),
            ("Contact Ratio", "Kavrama Oranı Grafiği", self.generate_face_contact_graph),
            ("3D View", "3D Görünüm", self.generate_gear_visualization)
        ]

        self.figures = {}
        self.axes = {}
        self.canvases = {}

        for key, title, command in graph_info:
            frame = ttk.Frame(graph_notebook, padding="5")
            graph_notebook.add(frame, text=title)
            self.graph_frames[key] = frame

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            if key == "3D View":
                ax = fig.add_subplot(111, projection='3d')
            else:
                ax = fig.add_subplot(111)

            self.figures[key] = fig
            self.axes[key] = ax

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
            self.canvases[key] = canvas

            button = ttk.Button(frame, text=f"{title} Oluştur/Güncelle", command=command, padding=8)
            button.pack(pady=5, side=tk.BOTTOM)

    def set_value(self, item_key_base, suffix, value, precision=4):
        """Hesaplanan değeri ilgili etikete (L veya R) formatlayarak yazar."""
        item_key = f"{item_key_base}{suffix}"
        # Ara değerleri de saklayalım (örn. sadece item numarası ile)
        self.values[item_key_base] = value # Son hesaplanan değeri sakla (L veya R olabilir)
        self.values[item_key] = value # L/R spesifik değeri sakla

        if item_key in self.result_labels:
            if isinstance(value, (int, float)):
                if math.isnan(value) or math.isinf(value):
                    self.result_labels[item_key].set(str(value))
                else:
                    self.result_labels[item_key].set(f"{value:.{precision}f}")
            else:
                self.result_labels[item_key].set(str(value))
        # else:
            # print(f"Uyarı: Sonuç etiketi anahtarı '{item_key}' bulunamadı.")

    def get_value(self, item_key_base, suffix=None):
        """Hesaplanan bir değeri alır. Suffix belirtilirse L/R spesifik değeri arar."""
        if suffix:
            key_specific = f"{item_key_base}{suffix}"
            if key_specific in self.values:
                return self.values[key_specific]
        # Suffix belirtilmezse veya spesifik değer yoksa temel anahtarı dene
        if item_key_base in self.values:
            return self.values[item_key_base]
        else:
            # print(f"Uyarı: Değer '{item_key_base}' (suffix: {suffix}) bulunamadı.")
            raise KeyError(f"Gerekli değer '{item_key_base}' (suffix: {suffix}) hesaplanmadı.")

    # --- Hesaplama Fonksiyonları ---
    def calculate_all(self):
        """Tüm hesaplamaları sırayla yapar."""
        self.values.clear() # Önceki değerleri temizle
        for key in self.result_labels:
            self.result_labels[key].set("-") # UI'ı temizle

        try:
            # 1. Girişleri al ve temel değerleri hesapla
            if not self.process_inputs(): return False

            # 2. SB1 Hesaplamalarını yap
            if not self.calculate_sb1(): return False

            # 3. SB2 Hesaplamalarını yap
            if not self.calculate_sb2(): return False

            # 4. SB3 Hesaplamalarını yap
            if not self.calculate_sb3(): return False

            messagebox.showinfo("Başarılı", "Hesaplamalar tamamlandı!")
            self.notebook.select(1) # SB1 sekmesini göster
            return True

        except KeyError as e:
            messagebox.showerror("Hesaplama Hatası", f"Gerekli bir ara değer bulunamadı: {e}. Hesaplama sırasını kontrol edin.")
            return False
        except ValueError as e:
             messagebox.showerror("Hesaplama Hatası", f"Hesaplama sırasında hata: {e}")
             return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename if exc_tb else 'N/A'
            line_num = exc_tb.tb_lineno if exc_tb else 'N/A'
            messagebox.showerror("Beklenmedik Hata", f"Hesaplama sırasında beklenmedik hata: {e}\nDosya: {fname}\nSatır: {line_num}")
            return False

    def process_inputs(self):
        """Girdi değerlerini alır, doğrular ve temel değişkenleri self.values'a ekler."""
        try:
            # Girişleri al
            inputs_str = {k: v.get() for k, v in self.input_vars.items()}
            inputs = {k: float(v) for k, v in inputs_str.items()}

            # Girdileri doğrula
            if inputs['Pd'] <= 0 or inputs['F'] <= 0 or inputs['rc'] <= 0 or inputs['n'] <= 0 or inputs['N'] <= 0:
                raise ValueError("Pitch, Yüz Genişliği, Kesici Yarıçapı ve Diş Sayıları pozitif olmalıdır.")
            if inputs['a0P'] < 0 or inputs['a0G'] < 0 or inputs['b0P'] < 0 or inputs['b0G'] < 0:
                 raise ValueError("Addendum ve Dedendum değerleri negatif olamaz.")

            # Temel değerleri self.values'a ata
            self.values.update(inputs) # Float değerleri ekle
            self.values['phi'] = math.radians(inputs['phi_deg'])
            self.values['shaft_angle'] = math.radians(inputs['shaft_angle_deg'])
            self.values['psi'] = math.radians(inputs['psi_deg'])

            # Diğer temel hesaplamalar (SB1 öncesi)
            self.values['p'] = math.pi / self.get_value('Pd')
            self.values['d'] = self.get_value('n') / self.get_value('Pd')
            self.values['D'] = self.get_value('N') / self.get_value('Pd')

            # Pitch Açıları (γ, Γ)
            n = self.get_value('n')
            N = self.get_value('N')
            shaft_angle = self.get_value('shaft_angle')
            if abs(shaft_angle - math.pi/2) < 1e-6: # 90 derece durumu
                tan_gamma_p = n / N
            else: # Genel durum
                 cos_shaft = math.cos(shaft_angle)
                 sin_shaft = math.sin(shaft_angle)
                 ratio_N_n = N / n
                 tan_gamma_p = safe_division(sin_shaft, (ratio_N_n + cos_shaft))
                 if math.isinf(tan_gamma_p): raise ValueError("Pitch açısı (gamma_p) hesaplanamadı (sıfıra bölme).")
            self.values['gamma_p'] = math.atan(tan_gamma_p)
            self.values['Gamma_G'] = shaft_angle - self.get_value('gamma_p')

            # Dış Koni Mesafesi (A0)
            d = self.get_value('d')
            sin_gamma_p = math.sin(self.get_value('gamma_p'))
            self.values['A0'] = safe_division(d, (2 * sin_gamma_p))
            if math.isinf(self.get_value('A0')): raise ValueError("A0 hesaplanamadı (sin_gamma_p sıfır?).")

            # İç Koni Mesafesi (Ai)
            self.values['Ai'] = self.get_value('A0') - self.get_value('F')

            # Ortalama Koni Mesafesi (Am)
            self.values['Am'] = self.get_value('A0') - self.get_value('F') / 2.0

            # Trigonometrik Değerler
            self.values['sin_phi'] = math.sin(self.get_value('phi'))
            self.values['cos_phi'] = math.cos(self.get_value('phi'))
            self.values['tan_phi'] = math.tan(self.get_value('phi'))
            self.values['sin_psi'] = math.sin(self.get_value('psi'))
            self.values['cos_psi'] = math.cos(self.get_value('psi'))
            self.values['tan_psi'] = math.tan(self.get_value('psi'))
            self.values['sin_gamma_p'] = math.sin(self.get_value('gamma_p'))
            self.values['cos_gamma_p'] = math.cos(self.get_value('gamma_p'))
            self.values['tan_gamma_p'] = math.tan(self.get_value('gamma_p'))
            self.values['sin_Gamma_G'] = math.sin(self.get_value('Gamma_G'))
            self.values['cos_Gamma_G'] = math.cos(self.get_value('Gamma_G'))
            self.values['tan_Gamma_G'] = math.tan(self.get_value('Gamma_G'))

            # Dedendum Açıları (delta_p, delta_G)
            A0 = self.get_value('A0')
            b0P = self.get_value('b0P')
            b0G = self.get_value('b0G')
            tan_delta_p = safe_division(b0P, A0)
            tan_delta_G = safe_division(b0G, A0)
            if math.isinf(tan_delta_p) or math.isinf(tan_delta_G): raise ValueError("Dedendum açısı tanjantı hesaplanamadı (A0 sıfır?).")
            self.values['delta_p'] = math.atan(tan_delta_p)
            self.values['delta_G'] = math.atan(tan_delta_G)
            self.values['tan_delta_p'] = tan_delta_p # Tanjantları da sakla
            self.values['tan_delta_G'] = tan_delta_G
            self.values['sin_delta_p'] = math.sin(self.get_value('delta_p'))
            self.values['cos_delta_p'] = math.cos(self.get_value('delta_p'))
            self.values['sin_delta_G'] = math.sin(self.get_value('delta_G'))
            self.values['cos_delta_G'] = math.cos(self.get_value('delta_G'))

            #return True

            # Boşluk (Clearance) Hesaplaması (c)
            c_outer1 = self.get_value('b0P') - self.get_value('a0G')
            c_outer2 = self.get_value('b0G') - self.get_value('a0P')
            c_clearance = (c_outer1 + c_outer2) / 2.0
            if c_clearance < 0:
                print("Uyarı: Hesaplanan boşluk (clearance) negatif. Add/Ded değerlerini kontrol edin.")
                # Negatif boşluk genellikle hatadır, ancak hesaplamaya devam edilebilir.
                # c_clearance = 0 # Veya sıfıra ayarlanabilir
            self.values['c_clearance'] = c_clearance # Değeri sakla

            return True

        except (ValueError, TypeError) as e:
            messagebox.showerror("Giriş Hatası", f"Geçersiz giriş değeri: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Giriş İşleme Hatası", f"Girdiler işlenirken hata: {e}")
            return False

    def calculate_sb1(self):
        """SB1 Hesaplamalarını Gleason PDF'e göre yapar."""
        try:
            # --- Öğeleri Hesapla ve Kaydet ---
            # Öğeler 1-4 (Girişlerden)
            self.set_value('1', 'L', self.get_value('n'), precision=0)
            self.set_value('1', 'R', self.get_value('N'), precision=0)
            self.set_value('2', 'L', self.get_value('Pd'))
            self.set_value('2', 'R', self.get_value('p')) # p için 'R' sütunu kullanılıyor gibi
            self.set_value('3', 'L', self.get_value('d'))
            self.set_value('3', 'R', self.get_value('D'))
            self.set_value('4', 'L', self.get_value('F'))
            self.set_value('4', 'R', self.get_value('F') / 2.0)

            # Öğeler 5-8 (Temel Hesaplamalar)
            self.set_value('5', 'L', self.get_value('A0')) # A0 tek değer
            self.set_value('5', 'R', self.get_value('A0'))
            self.set_value('6', 'L', self.get_value('Am')) # Am tek değer
            self.set_value('6', 'R', self.get_value('Am'))
            self.set_value('7', 'L', self.get_value('Ai')) # Ai tek değer
            self.set_value('7', 'R', self.get_value('Ai'))
            self.set_value('8', 'L', self.get_value('rc')) # rc tek değer
            self.set_value('8', 'R', self.get_value('rc'))

            # Öğeler 9-16 (Açılar ve Trigonometri)
            self.set_value('9', 'L', math.degrees(self.get_value('phi')), precision=2)
            self.set_value('10', 'L', self.get_value('sin_phi'))
            self.set_value('11', 'L', self.get_value('cos_phi'))
            self.set_value('12', 'L', self.get_value('tan_phi'))
            self.set_value('13', 'L', math.degrees(self.get_value('psi')), precision=2)
            self.set_value('14', 'L', self.get_value('sin_psi'))
            self.set_value('15', 'L', self.get_value('cos_psi'))
            self.set_value('16', 'L', self.get_value('tan_psi'))
            # Sağ sütunlar genellikle boş bırakılır veya aynı değer yazılır
            for i in range(9, 17): self.set_value(str(i), 'R', self.get_value(str(i), 'L'))


            # Öğeler 17-26 (Pitch Açıları, Add/Ded, Kalınlık)
            self.set_value('17', 'L', math.degrees(self.get_value('gamma_p')), precision=2)
            self.set_value('17', 'R', math.degrees(self.get_value('Gamma_G')), precision=2)
            self.set_value('18', 'L', self.get_value('sin_gamma_p'))
            self.set_value('18', 'R', self.get_value('sin_Gamma_G'))
            self.set_value('19', 'L', self.get_value('cos_gamma_p'))
            self.set_value('19', 'R', self.get_value('cos_Gamma_G'))
            self.set_value('20', 'L', self.get_value('tan_gamma_p'))
            self.set_value('20', 'R', self.get_value('tan_Gamma_G'))
            self.set_value('21', 'L', self.get_value('a0P'))
            self.set_value('21', 'R', self.get_value('a0G'))
            self.set_value('22', 'L', self.get_value('b0P'))
            self.set_value('22', 'R', self.get_value('b0G'))
            self.set_value('23', 'L', math.degrees(self.get_value('delta_p')), precision=2)
            self.set_value('23', 'R', math.degrees(self.get_value('delta_G')), precision=2)
            self.set_value('24', 'L', self.get_value('cos_delta_p'))
            self.set_value('24', 'R', self.get_value('cos_delta_G'))
            self.set_value('25', 'L', self.get_value('tan_delta_p'))
            self.set_value('25', 'R', self.get_value('tan_delta_G'))
            self.set_value('26', 'L', self.get_value('t0PL')) # Girdi olarak alındı
            self.set_value('26', 'R', self.get_value('t0G'))  # Girdi olarak alındı

            # Öğeler 27-29 (Ara Hesaplamalar)
            val_27 = 2 * self.get_value('rc') * self.get_value('sin_psi') - self.get_value('A0')
            self.set_value('27', 'L', val_27)
            self.set_value('27', 'R', val_27)

            val_28 = val_27 + self.get_value('A0') # PDF Formülü: Öğe27 + A0
            self.set_value('28', 'L', val_28)
            self.set_value('28', 'R', val_28)

            Ai = self.get_value('Ai')
            A0 = self.get_value('A0')
            val_29 = safe_division(A0 * val_27, Ai) + Ai # PDF Formülü: (A0 * Öğe27) / Ai + Ai
            if math.isinf(val_29): raise ValueError("Öğe 29 hesaplanamadı (Ai sıfır?).")
            self.set_value('29', 'L', val_29)
            self.set_value('29', 'R', val_29)

            # Öğeler 30-35 (Dış/İç Spiral Açıları)
            rc = self.get_value('rc')
            sin_Psi_o_val = safe_division(val_28, 2 * rc)
            sin_Psi_o = max(-1.0, min(1.0, sin_Psi_o_val)) # Clamp
            if math.isinf(sin_Psi_o): raise ValueError("Öğe 30 hesaplanamadı (rc sıfır?).")
            self.set_value('30', 'L', sin_Psi_o)
            self.set_value('30', 'R', sin_Psi_o)
            Psi_o = safe_asin(sin_Psi_o)
            self.values['Psi_o'] = Psi_o # radyan
            self.set_value('31', 'L', math.degrees(Psi_o), precision=2)
            self.set_value('31', 'R', math.degrees(Psi_o), precision=2)
            self.set_value('32', 'L', math.degrees(Psi_o), precision=2) # PDF'teki tekrar?
            self.set_value('32', 'R', math.degrees(Psi_o), precision=2)

            sin_Psi_i_val = safe_division(val_29, 2 * rc)
            sin_Psi_i = max(-1.0, min(1.0, sin_Psi_i_val)) # Clamp
            if math.isinf(sin_Psi_i): raise ValueError("Öğe 33 hesaplanamadı (rc sıfır?).")
            self.set_value('33', 'L', sin_Psi_i)
            self.set_value('33', 'R', sin_Psi_i)
            Psi_i = safe_asin(sin_Psi_i)
            self.values['Psi_i'] = Psi_i # radyan
            self.set_value('34', 'L', math.degrees(Psi_i), precision=2)
            self.set_value('34', 'R', math.degrees(Psi_i), precision=2)
            cos_Psi_i = math.cos(Psi_i)
            self.values['cos_Psi_i'] = cos_Psi_i
            self.set_value('35', 'L', cos_Psi_i)
            self.set_value('35', 'R', cos_Psi_i)

            # Öğeler 36-40 (Boşluk, Dedendumlar)
            Pd = self.get_value('Pd')
            if Pd <= 1: Bmin, Bmax = 0.020, 0.030
            elif Pd <= 2: Bmin, Bmax = 0.012, 0.016 # PDF Tablosu
            elif Pd <= 3: Bmin, Bmax = 0.008, 0.011
            elif Pd <= 4: Bmin, Bmax = 0.006, 0.008 # PDF Tablosu
            elif Pd <= 6: Bmin, Bmax = 0.004, 0.006 # PDF Tablosu
            elif Pd <= 10: Bmin, Bmax = 0.002, 0.004
            else: Bmin, Bmax = 0.001, 0.003 # 20 ve üzeri
            self.set_value('36', 'L', Bmin)
            self.set_value('36', 'R', Bmax)
            self.values['Bmin'] = Bmin
            self.values['Bmax'] = Bmax

            F_half = self.get_value('4','R')
            b_P = self.get_value('b0P') - F_half * self.get_value('tan_delta_p')
            b_G = self.get_value('b0G') - F_half * self.get_value('tan_delta_G')
            self.set_value('37', 'L', b_P) # Pinyon (L)
            self.set_value('37', 'R', b_G) # Dişli (R)
            self.values['b_P'] = b_P
            self.values['b_G'] = b_G

            bi_P = b_P - F_half * self.get_value('tan_delta_p')
            bi_G = b_G - F_half * self.get_value('tan_delta_G')
            self.set_value('38', 'L', bi_P) # Pinyon (L)
            self.set_value('38', 'R', bi_G) # Dişli (R)
            self.values['bi_P'] = bi_P
            self.values['bi_G'] = bi_G

            val_39 = self.get_value('b0P') + self.get_value('b0G')
            self.set_value('39', 'L', val_39)
            self.set_value('39', 'R', val_39)

            val_40 = bi_P + bi_G
            self.set_value('40', 'L', val_40)
            self.set_value('40', 'R', val_40)

            # Öğeler 41-48 (Nokta Genişlikleri)
            val_41 = self.get_value('t0PL') # Formül: (A0 * t0PL) / A0 = t0PL
            self.set_value('41', 'L', val_41)
            # Sağ sütun PDF'te boş

            val_42 = safe_division(self.get_value('Ai') * self.get_value('p'), self.get_value('A0'))
            if math.isinf(val_42): raise ValueError("Öğe 42 hesaplanamadı (A0 sıfır?).")
            self.set_value('42', 'L', val_42) # PDF'te sadece sol sütun
            # Sağ sütun PDF'te boş

            # WG' (Dişli)
            cos_psi = self.get_value('cos_psi')
            tan_phi = self.get_value('tan_phi')
            b_G = self.get_value('37','R') # Dişli ortalama dedendumu
            val_43 = cos_psi * val_41 - 2 * tan_phi * b_G # Formül: (15)(41)-2(12)(37)R
            self.set_value('43', 'R', val_43) # WG' dişli için hesaplanır (R)
            self.values['WG_prime'] = val_43

            # WG, WRG (Öğe 44) - Metinden alınacak kurallar
            WG_prime = self.get_value('43', 'R')
            rc = self.get_value('rc')
            Pd = self.get_value('Pd')
            # WG Seçimi (Dişli Finiş)
            if rc == 1.75: # 3.5" kesici
                WG = round(WG_prime / 0.005) * 0.005
            else: # Diğer kesiciler (cut gear)
                WG = round(WG_prime / 0.010) * 0.010
            # WRG Seçimi (Dişli Kaba)
            if Pd >= 3: # 3 DP ve kaba
                WRG = WG - 0.030
            else: # Daha ince pitch
                WRG = WG - 0.020
            # Taşlanacaksa WRG = WG - <=0.010 (bu kodda taşlama durumu yok)
            self.set_value('44', 'L', WG) # Sol/Finish sütunu
            self.set_value('44', 'R', WRG) # Sağ/Rough sütunu
            self.values['WG'] = WG
            self.values['WRG'] = WRG

            # Wop (Pinyon)
            p = self.get_value('p')
            Psi_o = self.get_value('Psi_o') # radyan
            val_39_sum_b0 = self.get_value('39','L')
            # PDF Formülü: (2)R*(32)-2*(12)*(39)-(44)L -> p*Psi_o - 2*tan(phi)*(b0P+b0G)-WG
            # Boyutsal tutarsızlık var (açıdan uzunluk çıkarılıyor). Formül muhtemelen hatalı.
            # Geçici olarak hesaplamayı atlayıp 0 yazalım.
            val_45 = 0.0 # FORMÜL HATALI/BELİRSİZ
            self.set_value('45', 'L', val_45) # Wop pinyon için (L)
            self.values['Wop'] = val_45

            # Wip (Pinyon)
            cos_Psi_i = self.get_value('cos_Psi_i')
            val_40_sum_bi = self.get_value('40','L')
            # PDF Formülü: (42)*(35)-2*(12)*(40)-(44)L -> val_42*cos(Psi_i) - 2*tan(phi)*val_40 - WG
            val_46 = val_42 * cos_Psi_i - 2 * tan_phi * val_40_sum_bi - WG
            self.set_value('46', 'L', val_46) # Wip pinyon için (L)
            self.values['Wip'] = val_46

            # WLP (Pinyon)
            val_47 = min(val_45, val_46)
            self.set_value('47', 'L', val_47)
            self.values['WLP'] = val_47

            # WRP (Pinyon)
            #stock = self.get_value('stock_allowance', default=0.020) # Metinden veya varsayılan
            # WRP (Pinyon)
            # stock_allowance değerini burada tanımla
            stock_allowance = 0.020 # Varsayılan stok payı (PDF sayfa 6 referans alınarak)
            self.values['stock_allowance'] = stock_allowance
            val_47 = self.get_value('WLP')
            WRP_calc = val_47 - stock_allowance
            #WRP_calc = val_47 - stock
            # Yuvarlama
            if rc == 1.75: # 3.5" kesici
                WRP = round(WRP_calc / 0.005) * 0.005
            else:
                WRP = round(WRP_calc / 0.010) * 0.010
            # Minimum kontrolü (Metin sayfa 6)
            if rc >= 3.0 and WRP < 0.040: # 6" ve üstü için
                 WRP = 0.040
            self.set_value('48', 'L', WRP)
            self.values['WRP'] = WRP

            return True

        except KeyError as e:
            messagebox.showerror("SB1 Anahtar Hatası", f"SB1 için gerekli değer bulunamadı: {e}")
            return False
        except ValueError as e:
             messagebox.showerror("SB1 Değer Hatası", f"SB1 hesaplamasında geçersiz değer: {e}")
             return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename if exc_tb else 'N/A'
            line_num = exc_tb.tb_lineno if exc_tb else 'N/A'
            messagebox.showerror("SB1 Hatası", f"SB1 hesaplamasında hata: {e}\nDosya: {fname}\nSatır: {line_num}")
            return False

    def calculate_sb2(self):
        """SB2 Hesaplamalarını Gleason PDF'e göre yapar."""
        try:
            # Gerekli değerleri kontrol et
            required = ['Wop', 'Wip', 'rc', 'cos_psi', 'sin_phi', 'cos_phi', 'Ai', 'Bmax', 'A0', 'tan_phi',
                        'Gamma_G', 'bi_P', 'bi_G', 'c_clearance', 'n', 'cos_gamma_p', 'WLP', 'psi', 'delta_p',
                        'WG'] # ht eklendi
            for k in required: self.get_value(k) # Eksikse KeyError verir
# --- ht HESAPLAMASINI BURAYA TAŞIYIN ---
            # Öğe 82 ht (Tam Derinlik) - Boyut sayfasından alınır.
            htP = self.get_value('a0P') + self.get_value('b0P')
            htG = self.get_value('a0G') + self.get_value('b0G')
            self.set_value('82', 'L', htP)
            self.set_value('82', 'R', htG)
            self.values['htP'] = htP
            self.values['htG'] = htG
            # Öğe 49 WMP
            val_49 = max(self.get_value('Wop'), self.get_value('Wip'))
            self.set_value('49', 'L', val_49) # Genellikle pinyon için hesaplanır
            self.set_value('49', 'R', val_49)
            self.values['WMP'] = val_49

            # Öğe 50 WB - Tablo veya formül (Öğe 64'teki formülü kullanalım)
            # WB = WMP/2 + 0.003 ? (Sayfa 7'deki formül) -> Bu pinyon kesici için
            # Dişli için: WG'ye göre tablo (Sayfa 5/7). Şimdilik hesaplayalım.
            WB_calc = val_49 / 2.0 + 0.003
            # Tabloya göre yuvarlama/seçim yapılmalı. Şimdilik hesaplanan değeri kullanalım.
            self.set_value('50', 'L', WB_calc) # Pinyon için hesaplanan
            # Dişli için WG'ye göre tablo değeri gerekir. Şimdilik boş bırakalım veya hesaplayalım.
            # Örnek: WG=0.100 ise Tablodan WB=0.065 (T blade)
            # self.set_value('50', 'R', 0.065) # Örnek
            self.values['WB_P'] = WB_calc # Pinyon
            # self.values['WB_G'] = 0.065 # Dişli (Örnek)

            # Öğe 51
            val_51 = self.get_value('cos_psi')**2
            self.set_value('51', 'L', val_51)
            self.set_value('51', 'R', val_51)

            # Öğe 52
            val_52 = 1.0 - self.get_value('sin_phi')
            self.set_value('52', 'L', val_52)
            self.set_value('52', 'R', val_52)

            # Öğe 53
            val_53 = safe_division(val_52, self.get_value('cos_phi'))
            if math.isinf(val_53): raise ValueError("Öğe 53 hesaplanamadı (cos phi sıfır?).")
            self.set_value('53', 'L', val_53)
            self.set_value('53', 'R', val_53)

            # Öğe 54
            val_54 = safe_division(self.get_value('Ai') * self.get_value('Bmax'), self.get_value('A0'))
            if math.isinf(val_54): raise ValueError("Öğe 54 hesaplanamadı (A0 sıfır?).")
            self.set_value('54', 'L', val_54)
            self.set_value('54', 'R', val_54)

            # Öğe 55
            val_55 = safe_division(0.5 * val_54, self.get_value('tan_phi'))
            if math.isinf(val_55): raise ValueError("Öğe 55 hesaplanamadı (tan phi sıfır?).")
            self.set_value('55', 'L', val_55)
            self.set_value('55', 'R', val_55)

            # Öğe 56 c (iç boşluk) - Genellikle dış boşlukla aynı varsayılır
            # c = biP - aiG veya biG - aiP ? ai hesaplanmalı.
            # Veya dış boşluk c = b0P-a0G = b0G-a0P kullanılır.
            c_outer1 = self.get_value('b0P') - self.get_value('a0G')
            c_outer2 = self.get_value('b0G') - self.get_value('a0P')
            c_clearance = (c_outer1 + c_outer2) / 2.0
            self.set_value('56', 'L', c_clearance)
            self.set_value('56', 'R', c_clearance)
            self.values['c_clearance'] = c_clearance # Hem iç hem dış için aynı kabul edelim

            # Öğe 57 Ri (Pinyon için Sol Sütun)
            Ai = self.get_value('Ai')
            tan_Gamma = self.get_value('tan_Gamma_G')
            val_57 = safe_division(Ai * tan_Gamma, val_51) # val_51 = cos(psi)^2
            if math.isinf(val_57): raise ValueError("Öğe 57 hesaplanamadı (cos psi sıfır?).")
            self.set_value('57', 'L', val_57) # Pinyon Ri
            # Sağ sütun boş

            # Öğe 58 ai (Pinyon için Sol Sütun: bi_G - c)
            # Dişli iç dedendumu (bi_G) ve boşluk (c) kullanılır
            bi_G = self.get_value('bi_G')
            val_58_L = bi_G - c_clearance # Pinyonun iç addendumu ai_P = bi_G - c
            self.set_value('58', 'L', val_58_L)
            # Öğe 58 ai (Dişli için Sağ Sütun: bi_P - c)
            bi_P = self.get_value('bi_P')
            val_58_R = bi_P - c_clearance # Dişlinin iç addendumu ai_G = bi_P - c
            self.set_value('58', 'R', val_58_R)

            # Öğe 59
            n = self.get_value('n')
            N = self.get_value('N')
            cos_gamma_p = self.get_value('cos_gamma_p')
            cos_Gamma_G = self.get_value('cos_Gamma_G')
            val_59_L = safe_division(n, cos_gamma_p)
            val_59_R = safe_division(N, cos_Gamma_G)
            if math.isinf(val_59_L) or math.isinf(val_59_R): raise ValueError("Öğe 59 hesaplanamadı (cos pitch açısı sıfır?).")
            self.set_value('59', 'L', val_59_L)
            self.set_value('59', 'R', val_59_R)

            # Öğe 60
            val_60 = val_59_L + val_59_R
            self.set_value('60', 'L', val_60)
            self.set_value('60', 'R', val_60)

            # Öğe 61 Δa
            val_61 = safe_division(val_55 * val_59_L, val_60) # Pinyon için ΔaP
            val_61_R = safe_division(val_55 * val_59_R, val_60) # Dişli için ΔaG
            if math.isinf(val_61) or math.isinf(val_61_R): raise ValueError("Öğe 61 hesaplanamadı (Öğe 60 sıfır?).")
            self.set_value('61', 'L', val_61) # ΔaP
            self.set_value('61', 'R', val_61_R) # ΔaG

            # Öğe 62 (Referans)
            # PDF: 62L = 57R, 62R = 57L. Ancak 57R boştu. 57L Pinyon Ri idi.
            # Yüksek oranlı dişlilerde basitleştirme var (Sayfa 9).
            # Şimdilik R1 için Pinyon değerini (57L) kullanalım.
            R1_P = self.get_value('57','L')
            self.set_value('62', 'L', R1_P)
            self.set_value('62', 'R', R1_P) # Dişli için de aynı değeri kullanalım? Belirsiz.

            # Öğe 63 (Referans)
            # PDF: 63L = 61R, 63R = 61L
            self.set_value('63', 'L', val_61_R) # ΔaG
            self.set_value('63', 'R', val_61)   # ΔaP

            # Öğe 64 a1 (Düzeltilmiş İç Addendum)
            # a1_P = ai_P + Δa_G = 58L + 63L
            a1_P = val_58_L + val_61_R
            self.set_value('64', 'L', a1_P)
            # a1_G = ai_G + Δa_P = 58R + 63R
            a1_G = val_58_R + val_61
            self.set_value('64', 'R', a1_G)
            self.values['a1_P'] = a1_P
            self.values['a1_G'] = a1_G

            # Öğe 65 R1 (Düzeltilmiş Ri)
            # R1_P = Ri_P - Δa_G = 62L - 63L
            R1_P_corr = R1_P - val_61_R
            self.set_value('65', 'L', R1_P_corr)
            # R1_G = Ri_G - Δa_P = 62R - 63R
            # Ri_G belirsizdi, Ri_P kullanalım.
            R1_G_corr = R1_P - val_61
            self.set_value('65', 'R', R1_G_corr)
            self.values['R1_P_corr'] = R1_P_corr
            self.values['R1_G_corr'] = R1_G_corr

            # Öğe 66 R1/a1 Oranı
            ratio_P = safe_division(R1_P_corr, a1_P)
            ratio_G = safe_division(R1_G_corr, a1_G)
            if math.isinf(ratio_P) or math.isinf(ratio_G): raise ValueError("Öğe 66 hesaplanamadı (a1 sıfır?).")
            self.set_value('66', 'L', ratio_P)
            self.set_value('66', 'R', ratio_G)
            self.values['ratio_P'] = ratio_P
            self.values['ratio_G'] = ratio_G

            # Öğe 67 K1 (Grafik No. 1'den veya formülden)
            # Formülü kullanalım (Not: Grafik φ'ye bağlı, formülde yok?)
            # Formül R/a'ya bağlı görünüyor. Pinyon için hesaplayalım.
            phi = self.get_value('phi')
            R_a = ratio_P
            cos_phi = self.get_value('cos_phi')
            sin_phi = self.get_value('sin_phi')
            tan_phi = self.get_value('tan_phi')
            R_plus_a = R_a + 1 # a=1 normalizasyonu? Formülde R+a geçiyor.
            # Formüldeki 'a' addendum mu yoksa normalizasyon mu? Belirsiz. R/a = ratio_P kullanalım.
            acos_arg = safe_division(R_a * cos_phi, R_a + 1) # Formülde R+a, R/a+1 değil
            delta_phi_K1 = safe_acos(acos_arg) - phi
            term1 = delta_phi_K1
            term2 = (R_a + 1) * (delta_phi_K1 - math.sin(delta_phi_K1) + tan_phi * (1 - math.cos(delta_phi_K1)))
            K1_P = safe_division(cos_phi, 1 - sin_phi) * (term1 - term2)
            self.set_value('67', 'L', K1_P)
            # Dişli için de hesaplayalım
            R_a = ratio_G
            acos_arg = safe_division(R_a * cos_phi, R_a + 1)
            delta_phi_K1 = safe_acos(acos_arg) - phi
            term1 = delta_phi_K1
            term2 = (R_a + 1) * (delta_phi_K1 - math.sin(delta_phi_K1) + tan_phi * (1 - math.cos(delta_phi_K1)))
            K1_G = safe_division(cos_phi, 1 - sin_phi) * (term1 - term2)
            self.set_value('67', 'R', K1_G)
            self.values['K1_P'] = K1_P
            self.values['K1_G'] = K1_G


            # Öğe 68 ro (Taban Kenar Yarıçapı)
            ro_P = a1_P * K1_P
            ro_G = a1_G * K1_G
            self.set_value('68', 'L', ro_P)
            self.set_value('68', 'R', ro_G)
            self.values['ro_P'] = ro_P
            self.values['ro_G'] = ro_G

            # Öğe 69 Δr
            val_69 = safe_division(c_clearance - val_55, val_52)
            if math.isinf(val_69): raise ValueError("Öğe 69 hesaplanamadı (Öğe 52 sıfır?).")
            self.set_value('69', 'L', val_69)
            self.set_value('69', 'R', val_69)

            # Öğe 70 r1
            r1_P = ro_P + val_69
            r1_G = ro_G + val_69
            self.set_value('70', 'L', r1_P)
            self.set_value('70', 'R', r1_G)
            self.values['r1_P'] = r1_P
            self.values['r1_G'] = r1_G
            # Öğe 71 r2
            try:
                # WB_P'yi almayı dene (Öğe 50'de veya başka bir yerde hesaplanmış olabilir)
                WB_P = self.get_value('WB_P')
            except KeyError:
                # Bulunamazsa, başlangıçtaki tahmini veya başka bir varsayılanı kullan
                # Öğe 50'de saklanan başlangıç tahminini kullanalım
                WB_P = self.values.get('WB_initial', 0.1)
                # print("Uyarı: Öğe 71 için 'WB_P' bulunamadı, varsayılan kullanılıyor.")

            # val_53'ün önceden hesaplandığından emin ol (try-except bunu zaten yapar)
            val_53 = self.get_value('53', 'L') # Veya sadece '53'

            r2_P = safe_division(WB_P - 0.015, val_53)
            if math.isinf(r2_P): raise ValueError("Öğe 71 (Pinyon) hesaplanamadı (Öğe 53 sıfır?).")
            self.set_value('71', 'L', r2_P)
            # ... (Dişli için r2_G hesaplaması da benzer şekilde güncellenebilir) ...
            # Öğe 71 r2
            #WB_P = self.get_value('WB_P', default=0.1) # Hesaplanan veya varsayılan WB Pinyon
            #r2_P = safe_division(WB_P - 0.015, val_53)
            if math.isinf(r2_P): raise ValueError("Öğe 71 (Pinyon) hesaplanamadı (Öğe 53 sıfır?).")
            self.set_value('71', 'L', r2_P)
            # Dişli için WB_G gerekir (tablodan veya hesaplanmış)
            # WB_G = self.get_value('WB_G', default=0.1)
            # r2_G = safe_division(WB_G - 0.015, val_53)
            # self.set_value('71', 'R', r2_G)

            # Öğe 72
            WLP = self.get_value('WLP') # Pinyon Limit Nokta Genişliği
            val_72 = WLP - WB_P
            self.set_value('72', 'L', val_72) # Sadece pinyon için

            # Öğe 73
            val_73 = val_53 * val_72 + 0.001
            self.set_value('73', 'L', val_73)
            self.set_value('73', 'R', val_73)

            # Öğe 75
            val_75 = val_73 + 0.002
            self.set_value('75', 'L', val_75)
            self.set_value('75', 'R', val_75)

            # Öğe 74
            val_74 = safe_sqrt(val_75)
            self.set_value('74', 'L', val_74)
            self.set_value('74', 'R', val_74)

            # Öğe 76
            val_76 = val_73**2
            self.set_value('76', 'L', val_76)
            self.set_value('76', 'R', val_76)

            # Öğe 77 r3
            num_77 = 0.063 * val_74 + val_75
            r3 = safe_division(num_77, val_76)
            if math.isinf(r3): raise ValueError("Öğe 77 hesaplanamadı (Öğe 76 sıfır?).")
            self.set_value('77', 'L', r3)
            self.set_value('77', 'R', r3)
            self.values['r3'] = r3

            # Öğe 78 rE (Pinyon için)
            rE_P = min(r1_P, r2_P, r3)
            # PDF: Yuvarla (even 0.005"). Şimdilik yapmayalım.
            # Veya standart tablo yarıçapı kullanılır.
            self.set_value('78', 'L', rE_P)
            # Dişli için rE_G = min(r1_G, r2_G, r3) -> r2_G hesaplanmalı
            # self.set_value('78', 'R', rE_G)
            self.values['rE_P'] = rE_P
            # self.values['rE_G'] = rE_G

            # Öğe 79 #c' (Teorik kesici no)
            sin_psi = self.get_value('sin_psi')
            delta_p = self.get_value('delta_p') # radyan
            c_prime = safe_division(sin_psi * delta_p, 10.0) # PDF'te delta derece mi radyan mı? Radyan varsayalım.
            self.set_value('79', 'L', c_prime)
            self.set_value('79', 'R', c_prime)
            self.values['c_prime_theor'] = c_prime

            # Öğe 80 #CR (Kaba Kesici No) - Genellikle #c' ye yakın seçilir.
            self.set_value('80', 'L', f"Yakın {c_prime:.4f}")
            self.set_value('80', 'R', f"Yakın {c_prime:.4f}")

            # Öğe 81 #CF (Finiş Kesici No) - Metin: Spiral için #12, Zerol için #0 önerilir.
            # Spiral varsayalım.
            CF = 12.0 # Veya 0.0 Zerol için
            self.set_value('81', 'L', CF, precision=1)
            self.set_value('81', 'R', CF, precision=1)
            self.values['CF'] = CF

            # --- Sağ Sütun Hesaplamaları (SB2) ---
            # Öğe 82 ht (Tam Derinlik) - Boyut sayfasından alınır.
            # htP = a0P + b0P, htG = a0G + b0G
            htP = self.get_value('a0P') + self.get_value('b0P')
            htG = self.get_value('a0G') + self.get_value('b0G')
            self.set_value('82', 'L', htP)
            self.set_value('82', 'R', htG)
            self.values['htP'] = htP
            self.values['htG'] = htG

            # Öğe 83
            rc = self.get_value('rc')
            cos_psi = self.get_value('cos_psi')
            val_83 = safe_division(rc, cos_psi)
            if math.isinf(val_83): raise ValueError("Öğe 83 hesaplanamadı (cos psi sıfır?).")
            self.set_value('83', 'L', val_83)
            self.set_value('83', 'R', val_83)

            # Öğe 84
            A0 = self.get_value('A0')
            sin_psi = self.get_value('sin_psi')
            val_84 = A0 - rc * sin_psi
            self.set_value('84', 'L', val_84)
            self.set_value('84', 'R', val_84)

            # Öğe 85
            val_85 = val_83**2 + val_84**2
            self.set_value('85', 'L', val_85)
            self.set_value('85', 'R', val_85)

            # Öğe 86
            val_86 = safe_sqrt(val_85)
            self.set_value('86', 'L', val_86)
            self.set_value('86', 'R', val_86)

            # Öğe 87
            # Sol: (38)L + (58)R = bi_P + ai_G
            val_87_L = self.get_value('bi_P') + self.get_value('58','R')
            self.set_value('87', 'L', val_87_L)
            # Sağ: (82)R = htG
            val_87_R = self.get_value('htG')
            self.set_value('87', 'R', val_87_R)

            # Öğe 88
            WG = self.get_value('WG')
            tan_phi = self.get_value('tan_phi')
            val_88_L = 0.5 * WG + tan_phi * val_87_L
            val_88_R = 0.5 * WG + tan_phi * val_87_R # WG yerine WRG mi? Belirsiz. WG kullanalım.
            self.set_value('88', 'L', val_88_L)
            self.set_value('88', 'R', val_88_R)

            # Öğe 89
            val_89_L_plus = rc + val_88_L
            val_89_L_minus = rc - val_88_L
            val_89_R_plus = rc + val_88_R
            val_89_R_minus = rc - val_88_R
            self.set_value('89', 'L', f"+:{val_89_L_plus:.4f} -:{val_89_L_minus:.4f}")
            self.set_value('89', 'R', f"+:{val_89_R_plus:.4f} -:{val_89_R_minus:.4f}")
            self.values['89L+'] = val_89_L_plus
            self.values['89R+'] = val_89_R_plus # Artı değerler genelde kullanılır

            # Öğe 90 (Referans)
            Ai = self.get_value('Ai')
            A0 = self.get_value('A0')
            self.set_value('90', 'L', Ai)
            self.set_value('90', 'R', A0)

            # Öğe 91
            val_91_L = safe_division(val_86 * val_89_L_plus, 0.5)
            val_91_R = safe_division(val_86 * val_89_R_plus, 0.5)
            if math.isinf(val_91_L) or math.isinf(val_91_R): raise ValueError("Öğe 91 hesaplanamadı.")
            self.set_value('91', 'L', val_91_L)
            self.set_value('91', 'R', val_91_R)

            # Öğe 92 cos θ
            num_92_L = Ai**2 - val_89_L_plus**2 - val_85
            cos_theta_L_val = safe_division(num_92_L, val_91_L)
            if math.isinf(cos_theta_L_val): raise ValueError("Öğe 92 (L) hesaplanamadı (bölme).")
            cos_theta_L = max(-1.0, min(1.0, cos_theta_L_val))
            self.set_value('92', 'L', cos_theta_L)

            num_92_R = A0**2 - val_89_R_plus**2 - val_85
            cos_theta_R_val = safe_division(num_92_R, val_91_R)
            if math.isinf(cos_theta_R_val): raise ValueError("Öğe 92 (R) hesaplanamadı (bölme).")
            cos_theta_R = max(-1.0, min(1.0, cos_theta_R_val))
            self.set_value('92', 'R', cos_theta_R)
            self.values['cos_theta_L'] = cos_theta_L
            self.values['cos_theta_R'] = cos_theta_R

            # Öğe 93 θ
            theta_L = safe_acos(cos_theta_L) # radyan
            theta_R = safe_acos(cos_theta_R) # radyan
            self.set_value('93', 'L', math.degrees(theta_L), precision=2)
            self.set_value('93', 'R', math.degrees(theta_R), precision=2)
            self.values['theta_L'] = theta_L
            self.values['theta_R'] = theta_R

            # Öğe 94 Δθ
            delta_theta_deg = math.degrees(theta_L) - math.degrees(theta_R) - 1.0
            self.set_value('94', 'L', delta_theta_deg, precision=2)
            self.set_value('94', 'R', delta_theta_deg, precision=2) # Tek değer
            self.values['delta_theta_deg'] = delta_theta_deg

            # Öğe 95 Nb'
            Nb_prime = safe_division(360.0, delta_theta_deg) # Mutlak değer PDF'te yok
            if math.isinf(Nb_prime): raise ValueError("Öğe 95 hesaplanamadı (delta_theta sıfır?).")
            self.set_value('95', 'L', Nb_prime)
            self.set_value('95', 'R', Nb_prime)
            self.values['Nb_prime'] = Nb_prime

            # Öğe 96 NB (Standart seçimi)
            # PDF: Öğe 95'ten küçük sonraki standart. Tablo Sayfa 8/10.
            rc = self.get_value('rc')
            if rc <= 3.5: std_blades = [8, 12]
            elif rc <= 4.5: std_blades = [8]
            elif rc <= 5.0: std_blades = [12]
            elif rc <= 6.0: std_blades = [12, 16]
            elif rc <= 7.5: std_blades = [12, 16]
            elif rc <= 9.0: std_blades = [12, 16, 20]
            elif rc <= 12.0: std_blades = [12, 16, 20, 24, 28]
            else: std_blades = [12, 24, 32, 36]

            NB = 0
            # Nb_prime'dan küçük en büyük standart değeri bul
            # Nb_prime pozitif veya negatif olabilir. Pozitif varsayalım.
            possible_blades = sorted([b for b in std_blades if b < abs(Nb_prime)], reverse=True)
            if possible_blades:
                NB = possible_blades[0]
            else: # Uygun standart yoksa en küçüğünü al?
                NB = min(std_blades) if std_blades else 12 # Varsayılan

            self.set_value('96', 'L', NB, precision=0)
            self.set_value('96', 'R', NB, precision=0)
            self.values['NB'] = NB

            return True

        except KeyError as e:
            messagebox.showerror("SB2 Anahtar Hatası", f"SB2 için gerekli değer bulunamadı: {e}")
            return False
        except ValueError as e:
             messagebox.showerror("SB2 Değer Hatası", f"SB2 hesaplamasında geçersiz değer: {e}")
             return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename if exc_tb else 'N/A'
            line_num = exc_tb.tb_lineno if exc_tb else 'N/A'
            messagebox.showerror("SB2 Hatası", f"SB2 hesaplamasında hata: {e}\nDosya: {fname}\nSatır: {line_num}")
            return False

    def calculate_sb3(self):
        """SB3 Hesaplamalarını Gleason PDF'e göre yapar."""
        try:
            # Gerekli değerleri kontrol et
            required = ['tan_phi', 'b0G', 'WG', 'p', 'Psi_o', 'A0',
                        'tan_delta_G', 'tan_delta_p', 'a0P', '27', 'rc', 'Ai',
                        'Bmin', 'Bmax', 'd', 'F', 'Pd', 'cos_psi', 'sin_psi',
                        'cos_delta_p', 'sin_gamma_p', 'n', ]
            #required = ['tan_phi', 'b0G', 'WG', 'p', 'Psi_o',  'A0', # <-- 'sin_Psi_o' çıkarıldı
                        #'tan_delta_G', 'tan_delta_p', 'a0P', '27', 'rc', 'Ai', 
                        #'Bmin', 'Bmax',  'd', 'F', 'Pd', 'cos_psi', 'sin_psi'
                        #, 'cos_delta_p', 'sin_gamma_p', 'n',   'K2', 'S', ] # Ra, K2, S, beta_half, beta eklendi
            # Check if keys exist before getting them
            for k in required: self.get_value(k)
            delta_A = 0.0
            self.values['delta_A'] = delta_A 
            # Öğe 97
            tan_phi = self.get_value('tan_phi')
            b0G = self.get_value('b0G')
            WG = self.get_value('WG')
            val_97 = safe_division(tan_phi * b0G + WG, 0.5)
            self.set_value('97', 'L', val_97)
            self.set_value('97', 'R', val_97)

            # Öğe 98
            p = self.get_value('p')
            Psi_o = self.get_value('Psi_o') # radyan
            val_98 = p * Psi_o - val_97 # Boyutsal olarak hala şüpheli
            self.set_value('98', 'L', val_98)
            self.set_value('98', 'R', val_98)

            # Öğe 99
            #sin_Psi_o = self.get_value('sin_Psi_o')            
            sin_Psi_o = self.get_value('30', 'L')             
            val_99_L = safe_division(sin_Psi_o * val_97 + sin_Psi_o * val_98, 2.0) # Pinyon (L)
            val_99_R = safe_division(sin_Psi_o * val_97 - sin_Psi_o * val_98, 2.0) # Dişli (R)
            self.set_value('99', 'L', val_99_L)
            self.set_value('99', 'R', val_99_R)

            # Öğe 100 ΔA - Fonksiyonun başında tanımlandı ve self.values'a eklendi
            delta_A_val = self.get_value('delta_A') # Başta tanımlanan değeri al (default= GEREKMEZ)
            self.set_value('100', 'L', delta_A_val)
            self.set_value('100', 'R', delta_A_val)

            # Öğe 101
            val_101_L = max(val_99_L, delta_A)
            val_101_R = max(val_99_R, delta_A)
            self.set_value('101', 'L', val_101_L)
            self.set_value('101', 'R', val_101_R)

            # Öğe 102
            A0 = self.get_value('A0')
            val_102_L = A0 - val_101_L
            val_102_R = A0 - val_101_R
            self.set_value('102', 'L', val_102_L)
            self.set_value('102', 'R', val_102_R)

            # Öğe 103
            tan_delta_G = self.get_value('tan_delta_G')
            val_103 = val_101_R * tan_delta_G # 101R dişli değeri kullanılır
            self.set_value('103', 'R', val_103) # Sadece dişli için

            # Öğe 104
            tan_delta_p = self.get_value('tan_delta_p')
            val_104 = val_101_L * tan_delta_p # 101L pinyon değeri kullanılır
            self.set_value('104', 'L', val_104) # Sadece pinyon için

            # Öğe 105
            val_105 = safe_division(b0G - val_103, 0.5)
            self.set_value('105', 'R', val_105) # Sadece dişli için

            # Öğe 106
            val_106 = safe_division(tan_phi * val_105 + WG, 0.5)
            self.set_value('106', 'L', val_106) # PDF'te L sütununda
            self.set_value('106', 'R', val_106)

            # Öğe 107 (Referans)
            self.set_value('107', 'L', f"{val_97:.4f};{val_98:.4f}")
            self.set_value('107', 'R', f"{val_97:.4f};{val_98:.4f}")

            # Öğe 108
            a0P = self.get_value('a0P')
            val_108 = a0P - val_104 # val_104 pinyon için hesaplandı
            self.set_value('108', 'L', val_108) # Pinyon için

            # Öğe 109
            item27 = self.get_value('27')
            val_109 = A0 * item27 + val_102_L # val_102 pinyon için
            self.set_value('109', 'L', val_109)
            self.set_value('109', 'R', val_109) # R için de aynı mı?

            # Öğe 110 sin ΦM
            rc = self.get_value('rc')
            sin_PhiM_val = safe_division(val_109, 2 * rc)
            if math.isinf(sin_PhiM_val): raise ValueError("Öğe 110 hesaplanamadı (rc sıfır?).")
            sin_PhiM = max(-1.0, min(1.0, sin_PhiM_val))
            self.set_value('110', 'L', sin_PhiM)
            self.set_value('110', 'R', sin_PhiM)
            self.values['sin_PhiM'] = sin_PhiM

            # Öğe 111 ΦM
            PhiM = safe_asin(sin_PhiM) # radyan
            self.set_value('111', 'L', math.degrees(PhiM), precision=2)
            self.set_value('111', 'R', math.degrees(PhiM), precision=2)
            self.values['PhiM'] = PhiM

            # Öğe 112 cos ΦM
            cos_PhiM = math.cos(PhiM)
            self.set_value('112', 'L', cos_PhiM)
            self.set_value('112', 'R', cos_PhiM)
            self.values['cos_PhiM'] = cos_PhiM # Store for graph

            # Öğe 113
            p = self.get_value('p')
            val_113_R = p * cos_PhiM # Dişli (R) için
            self.set_value('113', 'R', val_113_R)

            # Öğe 114
            val_114 = safe_division(val_113_R * val_102_R, A0) # val_102 Dişli (R) için
            if math.isinf(val_114): raise ValueError("Öğe 114 hesaplanamadı (A0 sıfır?).")
            self.set_value('114', 'R', val_114) # Dişli (R) için

            # Öğe 115 tM (Ölçüm Kalınlığı)
            Bmin = self.get_value('Bmin')
            Bmax = self.get_value('Bmax')
            tM_min = val_106 - Bmin # 106L kullanılır PDF'te, val_106 L/R aynı
            tM_max = val_114 - val_106 # 106R kullanılır PDF'te
            self.set_value('115', 'L', tM_min) # Min (L)
            self.set_value('115', 'R', tM_max) # Max (R)
            self.values['tM_min'] = tM_min
            self.values['tM_max'] = tM_max
            self.values['tM'] = (tM_min + tM_max) / 2.0 # Ortalama bir değer saklayalım

            # Öğe 116
            val_116 = cos_PhiM**2 / 4.0
            self.set_value('116', 'L', val_116)
            self.set_value('116', 'R', val_116)

            # Öğe 117
            d = self.get_value('d')
            val_117 = safe_division(d * val_102_L, A0) # val_102 Pinyon (L) için
            if math.isinf(val_117): raise ValueError("Öğe 117 hesaplanamadı (A0 sıfır?).")
            self.set_value('117', 'L', val_117) # Pinyon (L) için

            # Öğe 118
            # tM kare için hangi değer? Min, Max, Ortalama? Ortalama kullanalım.
            tM_avg = self.get_value('tM')
            val_118 = safe_division(tM_avg**2, val_117)
            if math.isinf(val_118): raise ValueError("Öğe 118 hesaplanamadı (Öğe 117 sıfır?).")
            self.set_value('118', 'L', val_118) # Pinyon (L) için

            # Öğe 119
            cos_gamma_p = self.get_value('cos_gamma_p')
            val_119 = cos_gamma_p * val_118
            self.set_value('119', 'L', val_119) # Pinyon (L) için

            # Öğe 120 aM (Ölçüm Addendumu)
            val_120 = val_108 + val_116 * val_119
            self.set_value('120', 'L', val_120) # Pinyon (L) için
            self.values['aM'] = val_120 # Pinyon için Ölçüm Addendumu

            # --- Sağ Sütun (SB3 Roughing Settings) ---
            # Öğe 121 F*Pd
            F = self.get_value('F')
            Pd = self.get_value('Pd')
            val_121 = F * Pd
            self.set_value('121', 'L', val_121)
            self.set_value('121', 'R', val_121)

            # Öğe 122 mF (Grafik 2'den veya formülden)
            # Formülü kullanalım
            psi = self.get_value('psi')
            tan_psi = self.get_value('tan_psi')
            K1_mf = 0.3865
            K2_mf = 0.0171
            mF = (K1_mf * tan_psi - K2_mf * tan_psi**3) * val_121
            self.set_value('122', 'L', mF)
            self.set_value('122', 'R', mF)
            self.values['mF_calc'] = mF

            # Öğe 123 XB (Pinyon)
            tan_delta_p = self.get_value('tan_delta_p')
            b0P = self.get_value('b0P')
            XB_P = A0 * tan_delta_p - b0P
            self.set_value('123', 'L', XB_P) # Pinyon (L)
            self.values['XB_P'] = XB_P
            # Dişli için de hesaplayalım (metinde sadece pinyon gibi ama simetri?)
            tan_delta_G = self.get_value('tan_delta_G')
            b0G = self.get_value('b0G')
            XB_G = A0 * tan_delta_G - b0G
            self.set_value('123', 'R', XB_G) # Dişli (R)
            self.values['XB_G'] = XB_G

            # Öğe 124 V
            cos_psi = self.get_value('cos_psi')
            V = rc * cos_psi
            self.set_value('124', 'L', V)
            self.set_value('124', 'R', V)
            self.values['V'] = V

            # Öğe 125 H
            sin_psi = self.get_value('sin_psi')
            H = A0 - rc * sin_psi # PDF formülü
            self.set_value('125', 'L', H)
            self.set_value('125', 'R', H)
            self.values['H'] = H

            # Öğe 126 ctn q
            ctn_q = safe_division(H, V)
            if math.isinf(ctn_q): raise ValueError("Öğe 126 hesaplanamadı (V sıfır?).")
            self.set_value('126', 'L', ctn_q)
            self.set_value('126', 'R', ctn_q)
            self.values['ctn_q'] = ctn_q

            # Öğe 127 q
            q = math.atan2(V, H) # arccot(H/V) = arctan(V/H) -> atan2(V, H)
            self.set_value('127', 'L', math.degrees(q), precision=2)
            self.set_value('127', 'R', math.degrees(q), precision=2)
            self.values['q'] = q # radyan

            # Öğe 128 sin q
            sin_q = math.sin(q)
            self.set_value('128', 'L', sin_q)
            self.set_value('128', 'R', sin_q)
            self.values['sin_q'] = sin_q

            # Öğe 129 Ra (Pinyon)
            cos_delta_p = self.get_value('cos_delta_p')
            sin_gamma_p = self.get_value('sin_gamma_p')
            Ra_P = safe_division(cos_delta_p, sin_gamma_p)
            if math.isinf(Ra_P): raise ValueError("Öğe 129 (Pinyon) hesaplanamadı (sin gamma_p sıfır?).")
            self.set_value('129', 'L', Ra_P) # Pinyon (L)
            self.values['Ra_P'] = Ra_P
            # Dişli için de hesaplayalım (Ra_G)
            cos_delta_G = self.get_value('cos_delta_G')
            sin_Gamma_G = self.get_value('sin_Gamma_G')
            Ra_G = safe_division(cos_delta_G, sin_Gamma_G)
            if math.isinf(Ra_G): raise ValueError("Öğe 129 (Dişli) hesaplanamadı (sin Gamma_G sıfır?).")
            self.set_value('129', 'R', Ra_G) # Dişli (R)
            self.values['Ra_G'] = Ra_G

            # Öğe 130
            n = self.get_value('n')
            N = self.get_value('N')
            val_130_L = safe_division(n * Ra_P, 150.0)
            val_130_R = safe_division(N * Ra_G, 150.0) # Dişli için N ve Ra_G
            self.set_value('130', 'L', val_130_L)
            self.set_value('130', 'R', val_130_R)

            # Öğe 131 m75
            m75_L = 2 * val_130_L
            m75_R = 2 * val_130_R
            self.set_value('131', 'L', m75_L)
            self.set_value('131', 'R', m75_R)
            self.values['m75_L'] = m75_L
            self.values['m75_R'] = m75_R

            # Öğe 132 (Tablo)
            self.set_value('132', 'L', "Tablo")
            self.set_value('132', 'R', "Tablo")

            # Öğe 133 m50
            m50_L = 3 * val_130_L
            m50_R = 3 * val_130_R
            self.set_value('133', 'L', m50_L)
            self.set_value('133', 'R', m50_R)
            self.values['m50_L'] = m50_L
            self.values['m50_R'] = m50_R

            # Öğe 134 (Tablo)
            self.set_value('134', 'L', "Tablo")
            self.set_value('134', 'R', "Tablo")

            # Öğe 135 Test Roll
            # Varsayılan değerler: Cradle P:20, G:30
            cradle_roll_P = math.radians(20)
            cradle_roll_G = math.radians(30)
            work_roll_P = cradle_roll_P * Ra_P
            work_roll_G = cradle_roll_G * Ra_G
            self.set_value('135', 'L', f"C:20 W:{math.degrees(work_roll_P):.2f}")
            self.set_value('135', 'R', f"C:30 W:{math.degrees(work_roll_G):.2f}")
            self.values['work_roll_P'] = work_roll_P
            self.values['work_roll_G'] = work_roll_G

            # Öğe 136 S
            S = safe_division(V, sin_q)
            if math.isinf(S): raise ValueError("Öğe 136 hesaplanamadı (sin q sıfır?).")
            self.set_value('136', 'L', S)
            self.set_value('136', 'R', S)
            self.values['S'] = S

            # Öğe 137 Q
            q_deg = math.degrees(q)
            Q_LH = 360.0 - q_deg
            Q_RH = q_deg
            self.set_value('137', 'L', Q_LH, precision=2) # Sol El
            self.set_value('137', 'R', Q_RH, precision=2) # Sağ El
            self.values['Q_LH'] = Q_LH
            self.values['Q_RH'] = Q_RH

            # Öğe 138 K2 - Tablodan makineye göre alınmalı. Örnek: No. 116 = 8.75
            K2 = 8.75 # Örnek değer
            self.set_value('138', 'L', K2)
            self.set_value('138', 'R', K2)
            self.values['K2'] = K2

            # Öğe 139 sin(β/2)
            sin_beta_half_val = safe_division(S, 2 * K2)
            if math.isinf(sin_beta_half_val): raise ValueError("Öğe 139 hesaplanamadı (K2 sıfır?).")
            sin_beta_half = max(-1.0, min(1.0, sin_beta_half_val))
            self.set_value('139', 'L', sin_beta_half)
            self.set_value('139', 'R', sin_beta_half)
            self.values['sin_beta_half'] = sin_beta_half

            # Öğe 140 β/2
            beta_half = safe_asin(sin_beta_half) # radyan
            self.set_value('140', 'L', math.degrees(beta_half), precision=2)
            self.set_value('140', 'R', math.degrees(beta_half), precision=2)
            self.values['beta_half'] = beta_half # Store for graph maybe?

            # Öğe 141 β
            beta = 2 * beta_half # radyan
            self.set_value('141', 'L', math.degrees(beta), precision=2)
            self.set_value('141', 'R', math.degrees(beta), precision=2)
            self.values['beta'] = beta # Store for graph maybe?

            # Öğe 142 Q (Alternatif)
            Q_alt_LH = 270.0 + math.degrees(beta_half) - q_deg # Sol El (-)q
            Q_alt_RH = 270.0 + math.degrees(beta_half) + q_deg # Sağ El (+)q
            self.set_value('142', 'L', Q_alt_LH, precision=2) # Sol El
            self.set_value('142', 'R', Q_alt_RH, precision=2) # Sağ El
            self.values['Q_alt_LH'] = Q_alt_LH
            self.values['Q_alt_RH'] = Q_alt_RH

            # Öğe 143
            sqrt_arg = K2**2 - S**2
            val_143 = safe_sqrt(sqrt_arg)
            self.set_value('143', 'L', val_143)
            self.set_value('143', 'R', val_143)

            # Öğe 144 Q (Alternatif 2)
            Q_alt2_LH = 360.0 - Q_alt_LH
            Q_alt2_RH = 360.0 - Q_alt_RH
            self.set_value('144', 'L', Q_alt2_LH, precision=2) # Sol El
            self.set_value('144', 'R', Q_alt2_RH, precision=2) # Sağ El

            return True

        except KeyError as e:
            messagebox.showerror("SB3 Anahtar Hatası", f"SB3 için gerekli değer bulunamadı: {e}")
            return False
        except ValueError as e:
             messagebox.showerror("SB3 Değer Hatası", f"SB3 hesaplamasında geçersiz değer: {e}")
             return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename if exc_tb else 'N/A'
            line_num = exc_tb.tb_lineno if exc_tb else 'N/A'
            messagebox.showerror("SB3 Hatası", f"SB3 hesaplamasında hata: {e}\nDosya: {fname}\nSatır: {line_num}")
            return False

    # --- Grafik Fonksiyonları (PDF formüllerini kullanacak şekilde güncellendi) ---
    def generate_k1_graph(self):
        """K1 faktörü grafiğini ve hesaplanan noktayı çizer."""
        key = "K1 Factor"
        ax = self.axes[key]
        canvas = self.canvases[key]
        ax.clear()

        try:
            # Grafik verisi (R/a oranına göre K1 - PDF Formülü Uygulaması)
            R_a_ratios = np.logspace(-1, 1.5, 100) # 0.1 den ~30 a
            phi = self.get_value('phi') # Hesaplama yapılmadıysa varsayılan
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            tan_phi = math.tan(phi)
            k1_values = []

            for R_a in R_a_ratios:
                 if R_a <= 0: continue # Geçersiz oran
                 acos_arg = safe_division(R_a * cos_phi, R_a + 1.0)
                 delta_phi_K1 = safe_acos(acos_arg) - phi
                 term1 = delta_phi_K1
                 term2 = (R_a + 1.0) * (delta_phi_K1 - math.sin(delta_phi_K1) + tan_phi * (1.0 - math.cos(delta_phi_K1)))
                 K1 = safe_division(cos_phi, 1.0 - sin_phi) * (term1 - term2)
                 # K1 negatif çıkabilir mi? Formüle göre mümkün. Grafikte log ölçek sorun olabilir.
                 # Şimdilik mutlak değer alalım veya min 0 yapalım.
                 k1_values.append(max(1e-6, K1)) # Log için pozitif tut

            ax.loglog(R_a_ratios, k1_values, 'b-', label="K₁ Faktörü (PDF Formülü)")
            ax.grid(True, which="both", ls="--", alpha=0.6)
            ax.set_xlabel('R/a Oranı')
            ax.set_ylabel('K₁ Faktörü')
            ax.set_title('K₁ Faktörü (Yaklaşık)')

            # Hesaplanan noktayı işaretle (Pinyon için)
            if 'ratio_P' in self.values and 'K1_P' in self.values:
                ratio_p_calc = self.get_value('ratio_P')
                k1_p_calc = self.get_value('K1_P')
                if ratio_p_calc > 0 and k1_p_calc > 0:
                    ax.plot(ratio_p_calc, k1_p_calc, 'ro', markersize=7, label=f'Pinyon ({ratio_p_calc:.2f}, {k1_p_calc:.3f})')
                    ax.legend()

            canvas.draw()

        except KeyError:
             ax.text(0.5, 0.5, "SB2 Hesaplamaları Gerekli", ha='center', va='center', transform=ax.transAxes)
             canvas.draw()
        except Exception as e:
            messagebox.showerror("Grafik Hatası", f"K1 grafiği oluşturulurken hata: {e}")
            ax.text(0.5, 0.5, f"Grafik Hatası:\n{e}", ha='center', va='center', transform=ax.transAxes, color='red')
            canvas.draw()

    def generate_face_contact_graph(self):
        """Yüzey Kavrama Oranı grafiğini ve hesaplanan noktayı çizer."""
        key = "Contact Ratio"
        ax = self.axes[key]
        canvas = self.canvases[key]
        ax.clear()

        try:
            # Grafik verisi (PDF Grafik 2 altındaki formül)
            spiral_angles_deg = np.linspace(10, 50, 50)
            F_Pd_ratios = np.linspace(1, 14, 50)
            X, Y = np.meshgrid(spiral_angles_deg, F_Pd_ratios)

            tan_psi_grid = np.tan(np.radians(X))
            K1_mf = 0.3865
            K2_mf = 0.0171
            mf_grid = (K1_mf * tan_psi_grid - K2_mf * tan_psi_grid**3) * Y
            mf_grid = np.maximum(0.0, mf_grid) # Negatif olamaz

            levels = np.arange(0.5, 3.1, 0.25)
            contour = ax.contour(X, Y, mf_grid, levels=levels, colors='black', linestyles='dashed')
            ax.clabel(contour, inline=True, fontsize=8, fmt='%.2f')
            contour_filled = ax.contourf(X, Y, mf_grid, levels=levels, cmap='viridis', alpha=0.5)
            try:
                plt.colorbar(contour_filled, ax=ax, label='Yüzey Kavrama Oranı (mF - Yaklaşık)')
            except Exception as cb_err:
                print(f"Colorbar hatası: {cb_err}") # Colorbar bazen hata verebilir

            ax.set_xlabel('Ortalama Spiral Açısı (ψ) [°]')
            ax.set_ylabel('Yüz Genişliği × Diametral Pitch (F × Pd)')
            ax.set_title('Yaklaşık Yüzey Kavrama Oranı (mF)')
            ax.grid(True, ls='--', alpha=0.5)
            ax.set_ylim(bottom=min(F_Pd_ratios)) # Eksenin alttan başlamasını sağla

            # Hesaplanan noktayı işaretle
            if 'psi_deg' in self.values and '121' in self.values and 'mF_calc' in self.values:
                psi_calc_deg = self.get_value('psi_deg')
                fpd_calc = self.get_value('121', 'L') # Öğe 121
                mf_calc = self.get_value('mF_calc')
                if not math.isnan(psi_calc_deg) and not math.isinf(psi_calc_deg) and \
                   not math.isnan(fpd_calc) and not math.isinf(fpd_calc):
                    ax.plot(psi_calc_deg, fpd_calc, 'ro', markersize=7, label=f'Hesaplanan ({psi_calc_deg:.1f}°, {fpd_calc:.2f}, mF≈{mf_calc:.2f})')
                    ax.legend(loc='lower right')

            canvas.draw()

        except KeyError:
             ax.text(0.5, 0.5, "SB3 Hesaplamaları Gerekli", ha='center', va='center', transform=ax.transAxes)
             canvas.draw()
        except Exception as e:
            messagebox.showerror("Grafik Hatası", f"Kavrama Oranı grafiği oluşturulurken hata: {e}")
            ax.text(0.5, 0.5, f"Grafik Hatası:\n{e}", ha='center', va='center', transform=ax.transAxes, color='red')
            canvas.draw()

    def generate_gear_visualization(self):
        """Dişli ve pinyonun basitleştirilmiş 3D konik görünümünü oluşturur."""
        key = "3D View"
        ax = self.axes[key]
        canvas = self.canvases[key]
        ax.clear()

        try:
            # Gerekli değerleri kontrol et
            required_3d = ['d', 'D', 'A0', 'gamma_p', 'Gamma_G', 'n', 'N', 'shaft_angle_deg', 'Pd']
            if not all(k in self.values and not math.isnan(self.values[k]) and not math.isinf(self.values[k]) for k in required_3d):
                 ax.text(0.5, 0.5, 0.5, "Geçerli boyutları hesaplayın.", ha='center', va='center', transform=ax.transAxes)
                 canvas.draw()
                 return False

            d = self.get_value('d')
            D = self.get_value('D')
            A0 = self.get_value('A0')
            gamma_p = self.get_value('gamma_p') # radyan
            Gamma_G = self.get_value('Gamma_G') # radyan
            shaft_angle_deg = self.get_value('shaft_angle_deg')

            # Pitch Konilerini Çiz
            u = np.linspace(0, 2 * np.pi, 50) # Azimuthal açı
            dist = np.linspace(0, A0, 15)   # Koni boyunca mesafe
            U, Dist = np.meshgrid(u, dist)

            # Pinyon (Eksen Z'de varsayalım)
            Radius_p = Dist * math.sin(gamma_p)
            Zp = Dist * math.cos(gamma_p)
            Xp = Radius_p * np.cos(U)
            Yp = Radius_p * np.sin(U)

            # Dişli (Eksen Y'de varsayalım - 90 derece mil açısı için)
            # Genel açı durumu için döndürme matrisi gerekir, şimdilik 90 derece varsayalım
            if abs(shaft_angle_deg - 90.0) < 1.0: # Tolerans
                 Radius_G = Dist * math.sin(Gamma_G)
                 Yg = Dist * math.cos(Gamma_G) # Y ekseni boyunca yükseklik
                 Xg = Radius_G * np.cos(U)
                 Zg = Radius_G * np.sin(U)
                 ax.plot_surface(Xg, Yg, Zg, color='lightcoral', alpha=0.7)
            else:
                 ax.text(0, 0, 0.5, "3D Görünüm\nsadece 90° mil\naçısı için\ndestekleniyor.", ha='center', va='center', transform=ax.transAxes)


            ax.plot_surface(Xp, Yp, Zp, color='cyan', alpha=0.7)

            # Eksenleri ve Görünümü Ayarla
            max_range = A0 * 1.1
            if max_range <= 0 or math.isnan(max_range) or math.isinf(max_range): max_range = 10.0 # Fallback

            ax.set_xlim(-max_range, max_range)
            ax.set_ylim(-max_range, max_range)
            ax.set_zlim(-max_range, max_range)
            ax.set_xlabel("X Ekseni")
            ax.set_ylabel("Y Ekseni")
            ax.set_zlabel("Z Ekseni")
            ax.set_title(f'Pitch Konileri ({shaft_angle_deg:.0f}° Mil Açısı)')

            try: # Eşit ölçekleme
                ax.set_aspect('equal', adjustable='box')
            except NotImplementedError:
                 pass # Desteklenmiyorsa yoksay

            # Bilgi Metni
            n_val = self.get_value('n')
            N_val = self.get_value('N')
            Pd_val = self.get_value('Pd')
            text_str = f"Pinyon: {n_val:.0f}t, d={d:.2f}\n"
            text_str += f"Dişli: {N_val:.0f}t, D={D:.2f}\n"
            text_str += f"Mil Açısı: {shaft_angle_deg:.1f}°\n"
            text_str += f"Pitch: {Pd_val:.2f}"
            ax.text2D(0.05, 0.95, text_str, transform=ax.transAxes,
                       bbox=dict(facecolor='white', alpha=0.7), ha='left', va='top')

            canvas.draw()
            return True

        except Exception as e:
            print(f"3D Görünüm hatası: {str(e)}")
            ax.clear()
            ax.text(0.5, 0.5, 0.5, f"3D Görünüm Hatası:\n{e}", ha='center', va='center', transform=ax.transAxes, color='red')
            canvas.draw()
            return False


def main():
    """Ana uygulama fonksiyonu."""
    root = tk.Tk()
    # ttk teması kullan (isteğe bağlı)
    try:
        style = ttk.Style(root)
        themes = style.theme_names()
        # Platforma uygun tema seçimi
        if sys.platform == "win32" and 'vista' in themes:
            style.theme_use('vista')
        elif sys.platform == "darwin" and 'aqua' in themes: # macOS
             style.theme_use('aqua')
        elif 'clam' in themes: # Linux/Diğer
             style.theme_use('clam')
    except Exception:
        print("Varsayılan ttk teması kullanılıyor.")

    app = SpiralBevelCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

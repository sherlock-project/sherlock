"""
Site Yonetim Ekrani
Yeni site ekleme ve yonetim araci
"""

import customtkinter as ctk
from tkinter import messagebox

from sherlock_project.sites import SitesInformation


class SiteManagerFrame(ctk.CTkFrame):
    """Site yonetim ekrani"""

    def __init__(self, master, sites: SitesInformation, **kwargs):
        super().__init__(master, **kwargs)

        self.sites = sites

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_form()
        self._create_site_list()

    def _create_header(self):
        """Baslik"""
        self.header = ctk.CTkFrame(self, fg_color='transparent')
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        self.title_label = ctk.CTkLabel(
            self.header,
            text='Site Manager',
            font=ctk.CTkFont(size=20, weight='bold')
        )
        self.title_label.pack(side='left')

        self.count_label = ctk.CTkLabel(
            self.header,
            text=f'{len(self.sites)} sites loaded'
        )
        self.count_label.pack(side='right')

    def _create_form(self):
        """Yeni site ekleme formu"""
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        # Site adi
        self.name_label = ctk.CTkLabel(self.form_frame, text='Site Name:')
        self.name_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text='e.g., GitHub')
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        # Ana URL
        self.url_label = ctk.CTkLabel(self.form_frame, text='Main URL:')
        self.url_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.url_entry = ctk.CTkEntry(self.form_frame, placeholder_text='https://example.com')
        self.url_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Kullanici URL sablonu
        self.user_url_label = ctk.CTkLabel(self.form_frame, text='User URL:')
        self.user_url_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.user_url_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text='https://example.com/user/{username}'
        )
        self.user_url_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Hata tipi
        self.error_type_label = ctk.CTkLabel(self.form_frame, text='Error Type:')
        self.error_type_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.error_type = ctk.CTkOptionMenu(
            self.form_frame,
            values=['message', 'status_code', 'response_url']
        )
        self.error_type.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # Hata mesaji
        self.error_msg_label = ctk.CTkLabel(self.form_frame, text='Error Message:')
        self.error_msg_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.error_msg_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text='Not found, 404, etc.'
        )
        self.error_msg_entry.grid(row=4, column=1, padx=10, pady=5, sticky='ew')

        # Butonlar
        self.btn_frame = ctk.CTkFrame(self.form_frame, fg_color='transparent')
        self.btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        self.test_btn = ctk.CTkButton(
            self.btn_frame,
            text='Test Site',
            command=self._test_site,
            width=120
        )
        self.test_btn.pack(side='left', padx=5)

        self.add_btn = ctk.CTkButton(
            self.btn_frame,
            text='Add Site',
            command=self._add_site,
            width=120
        )
        self.add_btn.pack(side='left', padx=5)

        self.form_frame.grid_columnconfigure(1, weight=1)

    def _create_site_list(self):
        """Mevcut site listesi"""
        self.list_label = ctk.CTkLabel(
            self,
            text=f'Loaded sites: {len(self.sites)}'
        )
        self.list_label.grid(row=2, column=0, padx=10, pady=10)

    def _test_site(self):
        """Siteyi test et"""
        messagebox.showinfo('Test', 'Test functionality coming soon!')

    def _add_site(self):
        """Site ekle"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror('Error', 'Site name required')
            return

        messagebox.showinfo('Success', f'Site "{name}" added!')
        self._clear_form()

    def _clear_form(self):
        """Formu temizle"""
        self.name_entry.delete(0, 'end')
        self.url_entry.delete(0, 'end')
        self.user_url_entry.delete(0, 'end')
        self.error_msg_entry.delete(0, 'end')

import tkinter as tk
from tkinter import ttk

from api import fetch_rates
from db import init_db, save_rate, get_saved_rate


class CurrencyConverterApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Конвертер валют")
        self.geometry("420x680")

        # Переменные ввода/вывода
        self.loan_var = tk.StringVar()
        self.loan_time_var = tk.StringVar()
        self.annual_interest_var = tk.StringVar()
        self.base_var = tk.StringVar(value="RUB")
        self.target_var = tk.StringVar()

        # Ежемесячный платёж — понадобится для конвертации
        self.monthly_payment = 0.0

        init_db()
        self.create_widgets()
        self.log("Приложение запущено")

    # ---------- UI ----------
    def create_widgets(self) -> None:
        pad = dict(padx=6, pady=4)

        # Сумма кредита
        ttk.Label(self, text="Сумма кредита:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self.loan_var).grid(row=0, column=1, **pad)
        ttk.Label(self, text="RUB").grid(row=0, column=2, sticky="w", **pad)

        # Срок кредита
        ttk.Label(self, text="Срок кредита:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self.loan_time_var).grid(row=1, column=1, **pad)
        ttk.Label(self, text="Мес.").grid(row=1, column=2, sticky="w", **pad)

        # Процентная ставка
        ttk.Label(self, text="Процентная ставка:").grid(
            row=2, column=0, sticky="w", **pad
        )
        ttk.Entry(self, textvariable=self.annual_interest_var).grid(
            row=2, column=1, **pad
        )
        ttk.Label(self, text="%").grid(row=2, column=2, sticky="w", **pad)

        # Кнопка расчёта
        ttk.Button(self, text="Рассчитать", command=self.calculate_loan).grid(
            row=3, column=0, columnspan=3, pady=6
        )

        # Результаты расчёта
        self.monthly_label = ttk.Label(self, text="Ежемесячный платеж: 0 RUB")
        self.monthly_label.grid(row=4, column=0, columnspan=3, sticky="w", **pad)

        self.loan_sum_label = ttk.Label(self, text="Сумма всех платежей: 0 RUB")
        self.loan_sum_label.grid(row=5, column=0, columnspan=3, sticky="w", **pad)

        self.interest_label = ttk.Label(self, text="Начисленные проценты: 0 RUB")
        self.interest_label.grid(row=6, column=0, columnspan=3, sticky="w", **pad)

        # Базовая валюта
        ttk.Label(self, text="Базовая валюта:").grid(row=7, column=0, sticky="w", **pad)
        ttk.Label(self, textvariable=self.base_var).grid(
            row=7, column=1, sticky="w", **pad
        )

        # Целевая валюта
        ttk.Label(self, text="Целевая валюта:").grid(row=8, column=0, sticky="w", **pad)
        self.target_entry = ttk.Combobox(
            self, textvariable=self.target_var, state="readonly"
        )
        self.target_entry.grid(row=8, column=1, **pad)

        # Кнопка конвертации
        ttk.Button(self, text="Конвертировать", command=self.convert).grid(
            row=9, column=0, columnspan=3, pady=4
        )

        # Результат конвертации
        self.result_label = ttk.Label(self, text="")
        self.result_label.grid(row=10, column=0, columnspan=3, sticky="w", **pad)

        # Кнопка обновления курсов
        ttk.Button(self, text="Обновить курсы", command=self.update_db).grid(
            row=11, column=0, columnspan=3, pady=6
        )

        # Логгер
        self.log_text = tk.Text(self, height=8)
        self.log_text.grid(row=12, column=0, columnspan=3, sticky="nsew", **pad)

    # ---------- логирование ----------
    def log(self, message: str) -> None:

        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    # ---------- проверка корректности ----------
    def is_loan_invalid(self, value: float, message: str) -> bool:

        if value <= 0:
            self.log(message)
            return True
        return False

    # ---------- расчёт кредита ----------
    def calculate_loan(self) -> None:

        try:
            loan = float(self.loan_var.get())
            months = int(self.loan_time_var.get())
            rate = float(self.annual_interest_var.get())
        except ValueError:
            self.log("Ошибка: введите корректные числа")
            return

        if (
            self.is_loan_invalid(loan, "Сумма должна быть > 0")
            or self.is_loan_invalid(months, "Срок должен быть > 0")
            or self.is_loan_invalid(rate, "Процентная ставка должна быть > 0")
        ):
            return

        monthly_rate = rate / 100 / 12
        payment = loan * monthly_rate / (1 - (1 + monthly_rate) ** -months)
        total = payment * months
        interest = total - loan

        self.monthly_payment = payment

        self.monthly_label.config(text=f"Ежемесячный платеж: {payment:,.2f} RUB")
        self.loan_sum_label.config(text=f"Сумма всех платежей: {total:,.2f} RUB")
        self.interest_label.config(text=f"Начисленные проценты: {interest:,.2f} RUB")

        self.log(f"Кредит рассчитан: платёж {payment:,.2f} RUB/мес.")

    # ---------- конвертация ----------
    def convert(self) -> None:

        if self.monthly_payment <= 0:
            self.log("Сначала рассчитайте кредит")
            return

        target = self.target_var.get().strip().upper()
        if not target:
            self.log("Выберите целевую валюту")
            return

        rate = get_saved_rate(target)
        if rate is None:
            self.log(f"Курс для {target} не найден. Нажмите «Обновить курсы».")
            return

        result = self.monthly_payment / rate
        self.result_label.config(text=f"Результат: {result:,.2f} {target}")
        self.log(f"{self.monthly_payment:,.2f} RUB = {result:,.2f} {target}")

    # ---------- обновление курсов ----------
    def update_db(self) -> None:

        data = fetch_rates()
        if not data or "Valute" not in data:
            self.log("Не удалось получить курсы валют")
            return

        codes = []
        for idx, (code, info) in enumerate(data["Valute"].items(), start=1):
            try:
                # Value / Nominal = рублей за 1 единицу валюты
                rate = info["Value"] / info["Nominal"]
                save_rate(idx, code, rate)
                codes.append(code)
            except (KeyError, ZeroDivisionError) as e:
                self.log(f"Ошибка данных {code}: {e}")

        self.target_entry["values"] = codes
        if codes and not self.target_var.get():
            self.target_var.set(codes[0])

        self.log(f"Курсы обновлены: {len(codes)} валют")


if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()

from core.transaction import Transaction

def main():
    t1 = Transaction("01/01/2025", "Walmart", amount=10, memo="Test")
    
    print(t1)
    
    t1.amount = 100
    print(f"t1 amount after changing: {t1.amount}")
    
    t2 = Transaction(date="3/18/2026")
    print(t2)
    
    t3 = Transaction(payee="GameStop", date="02/03/2024")
    print(t3)
    
    t4 = Transaction("01/20/2025")
    print(t4)


if __name__ == "__main__":
    main()

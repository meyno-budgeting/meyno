from core.transaction import Transaction

def test_constructors():
    inDate = "01/01/2025"
    inPayee = "TestPayee"
    inCategory = "TestAccount"
    inAmount = 100
    inMemo = "TestMemo"
    
    expectedPayee = "TestPayee"
    expectedCategory = "TestAccount"
    expectedAmount = 100
    expectedMemo = "TestMemo"
    
    t = Transaction(inDate, inPayee, inCategory, inAmount, inMemo)
    
    assert t.payee == expectedPayee
    assert t.category == expectedCategory
    assert t.amount == expectedAmount
    assert t.memo == expectedMemo
    
    t2 = Transaction(inDate)
    
    expectedPayee = ""
    expectedCategory = "Uncategorized"
    expectedAmount = 0.00
    expectedMemo = ""
    
    assert t2.payee == expectedPayee
    assert t2.category == expectedCategory
    assert t2.amount == expectedAmount
    assert t2.memo == expectedMemo
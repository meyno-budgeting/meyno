from core.transaction import Transaction
import pytest

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
    
    t2.payee = "Walmart"
    t2.category = "Groceries"
    t2.amount = 3.98
    t2.memo = "Eggs"
    
    expectedPayee = "Walmart"
    expectedCategory = "Groceries"
    expectedAmount = 3.98
    expectedMemo = "Eggs"
    
    assert t2.payee == expectedPayee
    assert t2.category == expectedCategory
    assert t2.amount == expectedAmount
    assert t2.memo == expectedMemo
    
@pytest.fixture
def reset_date_format():
    old_format = Transaction.dateFormat
    yield
    Transaction.dateFormat = old_format
    
def test_date_formats(reset_date_format):
        inDate = "04/07/2025"
        t = Transaction(inDate)
        
        expectedDate = "04/07/2025"
        assert t.formattedDate() == expectedDate
        
        Transaction.dateFormat = "%d/%m/%Y"
        expectedDate = "07/04/2025"
        assert t.formattedDate() == expectedDate
        
        Transaction.dateFormat = "%Y/%m/%d"
        expectedDate = "2025/04/07"
        assert t.formattedDate() == expectedDate
        
        Transaction.dateFormat = "%b %d, %Y"
        expectedDate = "Apr 07, 2025"
        assert t.formattedDate() == expectedDate
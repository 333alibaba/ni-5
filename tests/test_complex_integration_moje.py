import pytest 
from src.manager import Manager
from src.models import Parameters, Bill, Tenant

def test_apartment_costs():
    manager = Manager(Parameters())
    manager.bills = []
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2-10-2025',
        settlement_year=2025,
        settlement_month=1,
        amount_pln=400.4,
        type='rent'
    ))

    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 400.4
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0
    assert manager.get_apartment_costs('test', 2025, 1) is None

def test_apartment_costs_invalid_month():
    manager = Manager(Parameters())
    
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2025, 13)
        
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2025, 0)

def test_create_apartment_settlement():
    manager = Manager(Parameters())
    manager.bills = []  
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-05-10',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=600.0,
        type='rent'
    ))
    
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 5)
    
    assert settlement is not None
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 5
    assert settlement.total_bills_pln == 600.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == 600.0
    
    settlement_empty = manager.create_apartment_settlement('apart-polanka', 2025, 6)
    
    assert settlement_empty is not None
    assert settlement_empty.apartment == 'apart-polanka'
    assert settlement_empty.year == 2025
    assert settlement_empty.month == 6
    assert settlement_empty.total_bills_pln == 0.0
    assert settlement_empty.total_rent_pln == 0.0
    assert settlement_empty.total_due_pln == 0.0

def test_create_tenant_settlements():
    manager = Manager(Parameters())
    manager.bills = []
    manager.tenants = []
    
    apartment_key = 'apart-polanka'
    manager.bills.append(Bill(
        apartment=apartment_key,
        date_due='2025-05-10',
        settlement_year=2025,
        settlement_month=5,
        amount_pln=600.0,
        type='rent'
    ))
    
    manager.tenants.append(Tenant(
        name='Jan Kowalski', 
        apartment=apartment_key,
        room='1',
        rent_pln=1000.0,
        deposit_pln=1000.0,
        date_agreement_from='2025-01-01',
        date_agreement_to='2025-12-31'
    ))
    manager.tenants.append(Tenant(
        name='Anna Nowak', 
        apartment=apartment_key,
        room='2',
        rent_pln=1000.0,
        deposit_pln=1000.0,
        date_agreement_from='2025-01-01',
        date_agreement_to='2025-12-31'
    ))
    
    settlements_2 = manager.create_tenant_settlements(apartment_key, 2025, 5)
    
    assert settlements_2 is not None
    assert len(settlements_2) == 2
    assert settlements_2[0].year == 2025
    assert settlements_2[0].month == 5
    assert settlements_2[0].bills_pln == 300.0
    assert settlements_2[1].bills_pln == 300.0
    
    manager.tenants = [Tenant(
        name='Jan Kowalski', 
        apartment=apartment_key,
        room='1',
        rent_pln=1000.0,
        deposit_pln=1000.0,
        date_agreement_from='2025-01-01',
        date_agreement_to='2025-12-31'
    )]
    settlements_1 = manager.create_tenant_settlements(apartment_key, 2025, 5)
    
    assert settlements_1 is not None
    assert len(settlements_1) == 1
    assert settlements_1[0].year == 2025
    assert settlements_1[0].bills_pln == 600.0

    manager.tenants = []
    settlements_0 = manager.create_tenant_settlements(apartment_key, 2025, 5)    
    
    assert settlements_0 is not None
    assert len(settlements_0) == 0
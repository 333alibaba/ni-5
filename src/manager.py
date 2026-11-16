from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key:str, year: int | None = None, month:int | None = None) -> float|None:
        if apartment_key not in self.apartments:
            return None

        if month is not None and not (1 <= month <= 12):
            raise ValueError("Nieprawidlowa wartosc")
        total = 0

        for bill in self.bills:
            if bill.apartment == apartment_key:
                if ((bill.settlement_year == year) or (year is None)) and ((bill.settlement_month == month) or (month is None)):
                    total+=bill.amount_pln

        return total

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            return None
            
        total_bills = self.get_apartment_costs(apartment_key, year, month) or 0.0
        
        from src.models import ApartmentSettlement
        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=0.0,  
            total_bills_pln=total_bills,
            total_due_pln=total_bills  
        )

    def create_tenant_settlements(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            return []
            
        active_tenants = [t for t in self.tenants if t.apartment == apartment_key]
        if not active_tenants:
            return []
            
        total_bills = self.get_apartment_costs(apartment_key, year, month) or 0.0
        share_per_tenant = total_bills / len(active_tenants)
        settlements = []
        for tenant in active_tenants:
            settlements.append(TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=f"{apartment_key}-{year}-{month}",
                month=month,
                year=year,
                rent_pln=0.0,
                bills_pln=share_per_tenant,
                total_due_pln=share_per_tenant,
                balance_pln=-share_per_tenant
            ))
            
        return settlements
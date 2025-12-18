def clean_address(address: str) -> str:
    if not address:
        return address
    return address.split(',')[0].strip()

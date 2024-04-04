// This is a comment
http_call myApi.GET("https://api.example.com/users" { "Authorization" -> "Bearer XYZ123" } BODY -> "param1=value1&param2=value2")

if (x > 10) then
    {
    print("Hello, World!");
    }
else
    {
    print("Goodbye, World!");
    }
end

for (i = 0; i < 10; i = i + 1;) do
    {
    print(i);
    }
end

while (x != 0) do
    {
    x = x - 1;
    }
end
contract SimpleWallet {
    var owner address;
    var balance int = 0;

    event Deposit(address from, int amount);
    event Withdrawal(address to, int amount);
    event Transfer(address from, address to, int amount);

    public function initialize(address _owner) {
        owner = _owner;
        print("Wallet created for ");
        print(owner);
    }

    public function deposit(int _amount) {
        balance = balance + _amount;
        emit Deposit(owner, _amount);
    }

    public function withdraw(int _amount) {
        if (_amount <= balance) then{
            balance = balance - _amount;
            emit Withdrawal(owner, _amount);
        } else {
            print("Insufficient balance");
        }end
    }

    public function transfer(address _to, int _amount) {
        if (_amount <= balance) then{
            balance = balance - _amount;
            emit Transfer(owner, _to, _amount);
        } else {
            print("Insufficient balance for transfer");
        }end
    }

    private function getBalance() returns (int) {
        return balance;
    }

    public function checkBalance() {
        _balance = getBalance();
        print("The balance is: ");
        print(_balance);
    }
}

var walletAddress = "0x1234567890abcdef1234567890abcdef12345678";
deploy SimpleWallet.initialize(walletAddress);

SimpleWallet.deposit(100);
SimpleWallet.checkBalance();
SimpleWallet.withdraw(50);
SimpleWallet.checkBalance();
SimpleWallet.transfer("0xabcdef1234567890abcdef1234567890abcdef12", 25);
SimpleWallet.checkBalance();

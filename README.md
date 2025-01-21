# ledger: the cli finance tool that's trying its best :>

hey! this is ledger, a command-line tool for tracking your money without the drama. it's simple, it works, and it won't judge you for buying that third coffee today.

## what even is this?

it's a **personal finance tracker** that:
• handles your transactions without making you hate spreadsheets
• gives you insights about where your money goes (*spoiler: probably coffee*)
• keeps things simple while still being actually useful

oh, and it's built in Python because sometimes the classics just work™.

## current status: making money moves

```bash
# add some damage to your wallet
ledger add 42.50 --category food --description "groceries (mostly snacks tbh)"

# see where all your money went
ledger list --category food --start-date 2024-01-01

# face the monthly truth
ledger summary --period monthly

# pretend to be organized with categories
ledger categories list
ledger categories add food
ledger categories remove food  # when you give up on cooking

# export data (for your tax person who definitely judges your spending)
ledger export --format csv
```

## getting this thing running

you'll need Python 3.8+ (*because we're not savages*).

### the easy way:
```bash
./install.sh  # magic happens here
```
now you've got `ledger` available everywhere. *congratulations on adulting!*

### the dev way:
for when you want to mess with the code:
```bash
python3 -m venv .venv
source .venv/activate
pip install -e ".[dev]"  # the square brackets are important, trust me
```

## dev stuff (for the brave)

if you're helping out (*thank you!*), here's what you need to know:
- we follow PEP 8 (*mostly*)
- type hints everywhere (*because TypeError is not a fun surprise*)
- actual docstrings (*future you will thank us*)
- tests that test things (*revolutionary, i know*)

### testing things:
```bash
pytest  # pray to the test gods
```

### type checking:
```bash
mypy finance_cli  # watch for angry red squiggles
```

## license

MIT License (*because sharing is caring*)

this readme was written while tracking expenses that definitely could have been avoided. *probably*. :>

happy tracking! >:>

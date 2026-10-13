CREATE TABLE IF NOT EXISTS transactions (
  id BIGSERIAL PRIMARY KEY,
  title VARCHAR(120) NOT NULL CHECK (length(trim(title)) > 0),
  amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
  type VARCHAR(10) NOT NULL CHECK (type IN ('INCOME', 'EXPENSE')),
  category VARCHAR(60) NOT NULL CHECK (length(trim(category)) > 0),
  transaction_date DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_transaction_date
  ON transactions (transaction_date DESC);

$ErrorActionPreference = "Stop"

uv run maturin develop --release
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

cargo test
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

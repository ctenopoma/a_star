use pyo3::{exceptions::PyValueError, prelude::*, wrap_pyfunction};

#[pyfunction]
fn validate_name(name: String) -> PyResult<String> {
    if name.trim().is_empty() {
        Err(PyValueError::new_err("name must not be empty"))
    } else {
        Ok(name)
    }
}

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate_name, m)?)?;
    Ok(())
}

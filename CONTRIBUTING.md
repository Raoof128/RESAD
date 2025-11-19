# Contributing to Solar Farm SCADA Lab

Thank you for your interest in contributing! We welcome improvements to the physics models, new attack scenarios, and HMI enhancements.

## Development Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Raoof128/RESAD.git
    cd RESAD
    ```

2.  **Install dependencies**:
    ```bash
    make install
    ```

3.  **Run the lab**:
    ```bash
    make run
    ```

## Pull Request Process

1.  Ensure all tests pass: `make test`
2.  Format your code: `make format`
3.  Update documentation if you change any logic.
4.  Open a Pull Request with a clear description of your changes.

## Coding Standards

- We use **Black** for code formatting.
- We use **Flake8** for linting.
- All new features must include unit tests.

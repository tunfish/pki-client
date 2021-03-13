include util.mk


# =============
# Configuration
# =============

$(eval pki-client  := $(venv)/bin/pki-client)


# =====
# Setup
# =====

# Install requirements for development.
setup-package: virtualenv-dev
	@test -e $(pki-client) || $(pip) install --upgrade --editable=.[service]

export SOURCE=pnnl/energyplusagent/
export CONFIG=pnnl/energyplusagent/config
export TAG=energyplus

./scripts/core/make-agent.sh

# To set the agent to autostart with the platform, pass "enable"
# to make-agent.sh: ./scripts/core/make-agent.sh enable


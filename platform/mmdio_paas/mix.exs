# GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.
defmodule MmdioPaaS.MixProject do
  use Mix.Project

  def project do
    [
      app: :mmdio_paas,
      version: "26.8.26",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger, :crypto],
      mod: {MmdioPaaS.Application, []}
    ]
  end

  defp deps do
    [
      {:ash, "~> 3.0 and >= 3.28.0"},
      {:ash_json_api, "~> 1.7"},
      {:ash_r2rml, github: "seanchatmangpt/ash_r2rml", ref: "067954ad406fd637fd47646bdb10c4580809c79d"},
      {:reactor, ">= 0.9.0"},
      {:bandit, "~> 1.0"}
    ]
  end
end

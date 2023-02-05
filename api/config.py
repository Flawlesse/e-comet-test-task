from decouple import Config, RepositoryEnv
ENV = Config(RepositoryEnv("/.env"))
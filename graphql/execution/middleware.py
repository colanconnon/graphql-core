import inspect
from functools import partial
from itertools import chain

from promise import Promise

MIDDLEWARE_RESOLVER_FUNCTION = 'resolve'


class MiddlewareManager(object):

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self._middleware_resolvers = list(get_middleware_resolvers(middlewares))
        self._cached_resolvers = {}

    def get_field_resolver(self, field_resolver):
        if field_resolver not in self._cached_resolvers:
            self._cached_resolvers[field_resolver] = middleware_chain(field_resolver, self._middleware_resolvers)

        return self._cached_resolvers[field_resolver]


middlewares = MiddlewareManager


def get_middleware_resolvers(middlewares):
    for middleware in middlewares:
        # If the middleware is a function instead of a class
        if inspect.isfunction(middleware):
            yield middleware
        if not hasattr(middleware, MIDDLEWARE_RESOLVER_FUNCTION):
            continue
        yield getattr(middleware, MIDDLEWARE_RESOLVER_FUNCTION)


def middleware_chain(func, middlewares):
    if not middlewares:
        return func
    middlewares = chain((func, make_it_promise), middlewares)
    last_func = None
    for middleware in middlewares:
        last_func = partial(middleware, last_func) if last_func else middleware

    return last_func


def make_it_promise(next, *a, **b):
    return Promise.resolve(next(*a, **b))
import elegy
from haiku.testing import transform_and_run
import jax.numpy as jnp
import jax
import utils
import tensorflow.keras as tfk


@transform_and_run
def test_basic():
    y_true = jnp.array([[1.0, 1.0], [0.9, 0.0]])
    y_pred = jnp.array([[1.0, 1.0], [1.0, 0.0]])

    # Using 'auto'/'sum_over_batch_size' reduction type.
    mape = elegy.losses.MeanAbsolutePercentageError()
    result = mape(y_true, y_pred)
    assert jnp.isclose(result, 2.78, rtol=0.01)

    # Calling with 'sample_weight'.
    assert jnp.isclose(mape(y_true, y_pred, sample_weight=jnp.array([0.1, 0.9])), 2.5, rtol=0.01)

    # Using 'sum' reduction type.
    mape = elegy.losses.MeanAbsolutePercentageError(reduction=elegy.losses.Reduction.SUM)

    assert jnp.isclose(mape(y_true, y_pred), 5.6, rtol=0.01)

    # Using 'none' reduction type.
    mape = elegy.losses.MeanAbsolutePercentageError(reduction=elegy.losses.Reduction.NONE)

    assert jnp.all(jnp.isclose(result, [0. , 5.6], rtol=0.01))

@transform_and_run
def test_function():

    y_true = jnp.array([[1.0, 1.0], [0.9, 0.0]])
    y_pred = jnp.array([[1.0, 1.0], [1.0, 0.0]])

    ## Standard MAPE
    mape_elegy =  elegy.losses.MeanAbsolutePercentageError()
    mape_tfk = tfk.losses.MeanAbsolutePercentageError()
    assert jnp.isclose(mape_elegy(y_true, y_pred), mape_tfk(y_true, y_pred), rtol=0.0001)

    ## MAPE using sample_weight
    assert jnp.isclose(mape_elegy(y_true, y_pred, sample_weight=jnp.array([1, 0])), mape_tfk(y_true, y_pred, sample_weight=jnp.array([1, 0])), rtol=0.0001)

    ## MAPE with reduction method: SUM
    mape_elegy = elegy.losses.MeanAbsolutePercentageError(reduction=elegy.losses.Reduction.SUM)
    mape_tfk = tfk.losses.MeanAbsolutePercentageError(reduction=tfk.losses.Reduction.SUM)
    assert jnp.isclose(mape_elegy(y_true, y_pred), mape_tfk(y_true, y_pred), rtol=0.0001)

    ## MAPE with reduction method: NONE
    mape_elegy = elegy.losses.MeanAbsolutePercentageError(reduction=elegy.losses.Reduction.NONE)
    mape_tfk = tfk.losses.MeanAbsolutePercentageError(reduction=tfk.losses.Reduction.NONE)
    assert jnp.all(jnp.isclose(mape_elegy(y_true, y_pred), mape_tfk(y_true, y_pred), rtol=0.0001))

    ## Prove the loss function 
    rng = jax.random.PRNGKey(42)
    y_true = jax.random.randint(rng, shape=(2, 3), minval=0, maxval=2)
    y_pred = jax.random.uniform(rng, shape=(2, 3))
    y_true = y_true.astype(y_pred.dtype)
    loss = elegy.losses.mean_percentage_absolute_error(y_true, y_pred)
    assert loss.shape == (2,)
    assert jnp.array_equal(loss, 100 * jnp.mean(jnp.abs((y_pred - y_true) / (jnp.clip(y_true, utils.EPSILON, None))), axis=-1))

if __name__ == '__main__':
    test_basic()
    test_function()
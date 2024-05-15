import numpy as np
import scipy.optimize
import scipy.signal
from matplotlib import pyplot as plt
from pydantic import BaseModel, ConfigDict
from lcls_tools.common.data_analysis.fit.method_base import MethodBase


class ProjectionFit(BaseModel):
    """
    1d fitting class that allows users to choose the model with which the fit is performed,
    and if prior assumptions (bayesian regression) about the data should be used when performing the fit.
        Additionally there is an option to visualize the fitted data and priors.
    -To perform a 1d fit, call fit_projection(projection_data={*data_to_fit*})
    ------------------------
    Arguments:
    model: MethodBase (this argument is a child class object of method base
        e.g GaussianModel & DoubleGaussianModel)
    visualize_priors: bool (shows plots of the priors and init guess distribution before fit)
    use_priors: bool (incorporates prior distribution information into fit)
    visualize_fit: bool (visualize the parameters as a function of the forward function
        from our model compared to distribution data)
    """

    # TODO: come up with better name
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: MethodBase
    use_priors: bool = False

    def normalize(self, data: np.ndarray) -> np.ndarray:
        """
        Normalize a 1d array by scaling and shifting data
        s.t. data is between 0 and 1
        """
        data_copy = data.copy()
        normalized_data = data_copy / (np.max(data))
        # TODO: consider if robust normalization method needed, sensitive to zeros in tails.
        # normalized_data_tuple = scipy.signal.normalize(data,np.max(data))
        # print(normalized_data_tuple)
        # normalized_data = normalized_data_tuple[0]
        return normalized_data

    # TODO: move normalize/unormalize to method base? (Chris?)
    def unnormalize_model_params(
        self, params_dict: dict, projection_data: np.ndarray
    ) -> np.ndarray:
        """
        Takes fitted and normalized params and returns them
        to unnormalized values i.e the true fitted values of the distribution
        """
        max_value = np.max(projection_data)
        length = len(projection_data)
        for key, val in params_dict.items():
            if "sigma" in key or "mean" in key:
                true_fitted_val = val * length
            else:
                true_fitted_val = val * max_value
            temp = {key: true_fitted_val}
            params_dict.update(temp)
        return params_dict

    def model_setup(self, projection_data=np.ndarray) -> None:
        """sets up the model and init_values/priors"""
        self.model.profile_data = projection_data

    def fit_model(self) -> scipy.optimize._optimize.OptimizeResult:
        """
        Fits model params to distribution data and plots the fitted params
        as a function of the model.
        Returns optimizeResult object
        """
        x = np.linspace(0, 1, len(self.model.profile_data))
        y = self.model.profile_data

        init_values = np.array(
            [self.model.init_values[name] for name in self.model.param_names]
        )

        res = scipy.optimize.minimize(
            self.model.loss,
            init_values,
            args=(x, y, self.use_priors),
            bounds=self.model.param_bounds,
        )

        return res  # TODO:optional argument to return fig,ax

    def fit_projection(self, projection_data: np.ndarray) -> dict:
        """
        type is dict[str, float]
        Wrapper function that does all necessary steps to fit 1d array.
        Returns a dictionary where the keys are the model params and their
        values are the params fitted to the data
        """
        assert len(projection_data.shape) == 1
        fitted_params_dict = {}
        normalized_data = self.normalize(projection_data)
        self.model_setup(projection_data=normalized_data)
        res = self.fit_model()
        for i, param in enumerate(self.model.param_names):
            fitted_params_dict[param] = (res.x)[i]
        self.model.fitted_params_dict = fitted_params_dict.copy()
        params_dict = self.unnormalize_model_params(fitted_params_dict, projection_data)
        return params_dict

    def plot_fit(self):
        # TODO: dont specify any style, create lines and text boxes that go into figure
        # TODO: resolve issues with using res.x
        x = np.linspace(0, 1, len(self.model.profile_data))
        y = self.model.profile_data
        fig, ax = plt.subplots()
        y_fit = self.model.forward(x, self.model.fitted_params_dict)
        ax.plot(x, y, label="data")
        ax.plot(x, y_fit, label="fit")

        textstr = "\n".join(
            [
                r"$\mathrm{%s}=%.2f$" % (key, val)
                for key, val in self.model.fitted_params_dict.items()
            ]
        )
        ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            verticalalignment="top",
        )
        return fig, ax

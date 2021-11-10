
## Walkthrough: Implementing and Integrating an Algorithm
Adding an algorithm to the `sleepy` library mainly consists of three steps:
Setting up the correct folder structure and adding the implementation to the
list of supported algorithms, exposing the user parameters of the algorithm
and implementing the interface provided in `sleepy.processing.processor.Algorithm`.
We will go through each step and create a new algorithm called "Walkthrough" as an
example for the integration. You can find the final implementation of the Walkthrough algorithm
under `sleepy/processing/algorithms/walkthrough`.

### Setup
Setting up our files, we first create a new sub-folder in `sleepy/processing/algorithms`.
Inside of that sub-folder we create two `.py` files: `__init__.py` and `walkthrough.py`,
the latter of which contains a name of your choice. Feel free to add more files or
sub-folders if needed.
Inside of `walkthough.py` we insert a coding-stub for our implementation which looks as follows:

```python
from sleepy.processing.processor import Algorithm

class Walkthrough(Algorithm):

    def __init__(self):
        self.name = "Walkthrough"

```

We will fill this stub with content in the next section.

### Parameters
Using `sleepy` algorithms we distinguish between two types of parameters: user parameters
and extract parameters. The former are parameters that the user can set before executing
the algorithm. The latter are parameters that we infer from the dataset as a whole at
runtime. This section shows you how to add user parameters to your implementation using the
"Walkthrough" example. Extract parameters are discussed in the next session, since they are
tightly coupled with the runtime implementation of the algorithm.

A user parameter in `sleepy` can be described with three properties: `title`, `fieldType`
and `default`. The property `title` controls with what label the parameter is presented to
the user. The property `fieldType` controls which type the parameter has. This helps guiding
the user not to enter any type of value, but only a value suitable for this parameter.
Lastly, the property `default` controls the initial value of the parameter, e.g. a suggestion
to the user or a common value for this parameter.
Knowing this, we now only need to tell the engine, which will call our algorithm at runtime,
which parameters we would like the user to see and control.
In `sleepy` we can expose a user parameter by declaring it as a public attribute to our class.
Since each algorithm inherits from `sleepy.processing.processor.Algorithm`, each algorithm
inherits the method `render` which ensures that the GUI contains the parameter if the user
selects our algorithm and further registers the attribute to the GUI, such that every time the user
changes the parameter, an update is applied to the attribute. Let us look at the following example
of a paramter `alpha` in our "Walkthrough" example:

```python
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter

class Walkthrough(Algorithm):

    def __init__(self):
        self.name = "Walkthrough"

        self.alpha = Parameter(
            title = "Integer parameter alpha",
            fieldType = int,
            default = 5
        )

```

Note that in order to declare a parameter, we need to import the corresponding
class via `from sleepy.processing.parameter import Parameter`. There is no limitation
to how many user parameters can be declared this way. At runtime the `Parameter` object
is removed from `Walkthrough` and replaced with the actual value of the parameter.
This parameter is now available to the `Walkthrough` class and can be used during runtime.

Then next section demonstrates how to implement the algorithm logic, which will conclude the
walkthough.

### Extract, Compute, Filter
In the preprocessing window of `sleepy`, the user can select a dataset from her disk,
a filter and an algorithm. If the user decides to execute the selection of those three,
the algorithm gets called at three different steps: `extract`, `compute`, `filter`.
The `extract` is supplied with the entire data across all epochs and channels. Note that the
data is filtered before this step, if the user selected a filter.
At this step the algorithm has an opportunity to calculate extract parameters. These parameters will
be available to the `compute` step. The `compute` step is supplied with the extract parameters
(if there are any) and a signal of type `sleepy.processing.signal.Signal`.
The signal contains the data of one channel in one epoch of
the dataset. For more information about the `Signal` class refer to its source code or to the implementation
of the `Massimini` algorithm.
The task of the `compute` step is compute the detected events for each of these signals
individually. Note that if the data consists of `m` epochs and `n` channels, then the
`compute` step is called `m * n` times. The results of this step are aggregated and a list of events
is inferred from them. This list contains instances of the `sleepy.gui.tagging.model.event.core.Event`
class and is supplied to the `filter` step. This step now has an overview of all events found and its task is
to filter the list by additional criteria that was not possible to calculate on the signal level. So far, there exist two types of events, `sleepy.gui.tagging.model.event.core.PointEvent` and `sleepy.gui.tagging.model.event.core.IntervalEvent`.
An event has direct access to the data in its epoch through its `sleepy.gui.tagging.model.datasource.DataSource`. You can access the
amplitude of a point event via `sleepy.gui.tagging.model.event.core.PointEvent.amplitude`.
To implement one of the above steps, override the corresponding method in you algorithm implementation.
The "Walkthrough" example does not implement a extract step but the compute and the filter step.
In the compute step each data point whose amplitude is between the user parameter values `alpha` and `beta`
is identified as an event. The filter step filters out the higher 50% of amplitude values.
The full example looks as follows:

```python
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class Walkthrough(Algorithm):

    def __init__(self):
        self.name = "Walkthrough"

        self.alpha = Parameter(
            title = "Integer parameter alpha",
            fieldType = int,
            default = 5
        )

        self.beta = Parameter(
            title = "Floating-point parameter beta",
            fieldType = float,
            default = 1.2
        )

    def compute(self, signal):

        # Declare an inner function that can be used as a filter
        def isEvent(sample):

            # Get the amplitude for a given sample value
            amplitude = signal.data[sample]

            # Returns true if the filter condition is satisfied
            return amplitude > self.alpha and amplitude < self.beta

        signalLength = len(signal.data)

        # List comprehension to filter all the samples that satisfy our filter
        # condition
        return np.array([ sample for sample in range(signalLength) if isEvent(sample) ])

    def filter(self, events, data):

        # Sort the events ascending by amplitude.
        sortedByAmplitude = sorted(events, key = lambda event: event.amplitude )

        # cut off the first 50% of the events
        return sortedByAmplitude[:len(sortedByAmplitude) // 2]
```

To implement the extract step you have to use the following template.

```python

    def extract(self, data):

        ...

        return param_1, ..., param_t

    def compute(self, param_1, ..., param_t, signal):

        ...

```

The extract method returns a list of parameters which is then passed to every
compute step call. Thus, these parameters must be matched (not necessarily by name)
in the compute method.

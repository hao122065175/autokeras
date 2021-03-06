from autokeras.constant import Constant
from autokeras.graph import Graph
from autokeras.layers import StubBatchNormalization, StubConv, StubDropout, StubPooling, StubDense, StubFlatten, \
    StubReLU, StubSoftmax


class ClassifierGenerator:
    def __init__(self, n_classes, input_shape):
        self.n_classes = n_classes
        self.input_shape = input_shape
        if len(self.input_shape) > 4:
            raise ValueError('The input dimension is too high.')
        if len(self.input_shape) < 2:
            raise ValueError('The input dimension is too low.')

    def _get_shape(self, dim_size):
        temp_list = [(dim_size,), (dim_size, dim_size), (dim_size, dim_size, dim_size)]
        return temp_list[len(self.input_shape) - 2]


class DefaultClassifierGenerator(ClassifierGenerator):
    def __init__(self, n_classes, input_shape):
        super().__init__(n_classes, input_shape)

    def generate(self, model_len=Constant.MODEL_LEN, model_width=Constant.MODEL_WIDTH):
        pooling_len = int(model_len / 4)
        graph = Graph(self.input_shape, False)
        temp_input_channel = self.input_shape[-1]
        output_node_id = 0
        for i in range(model_len):
            output_node_id = graph.add_layer(StubReLU(), output_node_id)
            output_node_id = graph.add_layer(StubConv(temp_input_channel, model_width, kernel_size=3), output_node_id)
            output_node_id = graph.add_layer(StubBatchNormalization(model_width), output_node_id)
            temp_input_channel = model_width
            if pooling_len == 0 or ((i + 1) % pooling_len == 0 and i != model_len - 1):
                output_node_id = graph.add_layer(StubPooling(), output_node_id)

        output_node_id = graph.add_layer(StubFlatten(), output_node_id)
        output_node_id = graph.add_layer(StubDropout(Constant.CONV_DROPOUT_RATE), output_node_id)
        output_node_id = graph.add_layer(StubDense(graph.node_list[output_node_id].shape[0], model_width),
                                         output_node_id)
        output_node_id = graph.add_layer(StubReLU(), output_node_id)
        output_node_id = graph.add_layer(StubDense(model_width, self.n_classes), output_node_id)
        graph.add_layer(StubSoftmax(), output_node_id)
        return graph

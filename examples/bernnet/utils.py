import numpy as np
import pgl
import paddle

def set_seed(seed):
    paddle.seed(seed)
    np.random.seed(seed)

def normalize(feat):
    return feat / np.maximum(np.sum(feat, -1, keepdims=True), 1)

def random_splits(dataset,seed, train_rate=0.6, val_rate=0.2, ):
    #print(dataset.y.shape[0])
    percls_trn = int(round(train_rate*dataset.y.shape[0]/dataset.num_classes))
    val_lb = int(round(val_rate*dataset.y.shape[0]))
    
    index = [i for i in range(0,dataset.y.shape[0])]
    num_classes = dataset.num_classes
    train_idx=[]
    rnd_state = np.random.RandomState(seed)
    for c in range(num_classes):
        class_idx = np.where(dataset.y == c)[0]
        if len(class_idx)<percls_trn:
            train_idx.extend(class_idx)
        else:
            train_idx.extend(rnd_state.choice(class_idx, percls_trn,replace=False))
    rest_index = [i for i in index if i not in train_idx]
    val_idx=rnd_state.choice(rest_index,val_lb,replace=False)
    test_idx=[i for i in rest_index if i not in val_idx]

    dataset.train_index = train_idx
    dataset.val_index = val_idx
    dataset.test_index = test_idx
    return dataset

def load_data(name, seed, normalized_feature=True):
    if name == 'cora':
        dataset = pgl.dataset.CoraDataset()
    elif name == "pubmed":
        dataset = pgl.dataset.CitationDataset("pubmed", symmetry_edges=True)
    elif name == "citeseer":
        dataset = pgl.dataset.CitationDataset("citeseer", symmetry_edges=True)
    else:
        raise ValueError(name + " dataset doesn't exists")

    dataset.graph.node_feat["words"] = normalize(dataset.graph.node_feat["words"])
    dataset.graph.tensor()

    dataset = random_splits(dataset, seed)

    train_index = dataset.train_index
    dataset.train_label = paddle.to_tensor(np.expand_dims(dataset.y[train_index], -1))
    dataset.train_index = paddle.to_tensor(np.expand_dims(train_index, -1))

    val_index = dataset.val_index
    dataset.val_label = paddle.to_tensor(np.expand_dims(dataset.y[val_index], -1))
    dataset.val_index = paddle.to_tensor(np.expand_dims(val_index, -1))

    test_index = dataset.test_index
    dataset.test_label = paddle.to_tensor(np.expand_dims(dataset.y[test_index], -1))
    dataset.test_index = paddle.to_tensor(np.expand_dims(test_index, -1))

    return dataset
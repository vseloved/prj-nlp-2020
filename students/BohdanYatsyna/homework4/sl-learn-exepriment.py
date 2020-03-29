from sklearn.datasets import load_iris
from sklearn import tree
import matplotlib

X, y = load_iris(return_X_y=True)
iris = load_iris()
clf = tree.DecisionTreeClassifier()

clf = clf.fit(X, y)

print(clf)
tree.plot_tree(clf.fit(iris.data, iris.target))


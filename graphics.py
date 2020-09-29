import sv
import vtk
# FROM https://github.com/SimVascular/SimVascular-Tests/blob/master/new-api-tests/graphics/graphics.py
def add_line(renderer, pt1, pt2, color=[1.0, 1.0, 1.0], width=2):
    line = vtk.vtkLineSource()
    line.SetPoint1(pt1)
    line.SetPoint2(pt2)
    line.Update()
    polydata = line.GetOutput()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(width)
    renderer.AddActor(actor)

def create_segmentation_geometry(renderer, segmentation, color=[1.0, 1.0, 1.0], show_cpts=False, show_center=False):
    ''' Create geometry for the segmentation points and control points.
    '''
    #print("---------- gr.create_segmentation_geometry ----------")
    coords = segmentation.get_points()
    num_pts = len(coords)
    #print("[gr.create_segmentation_geometry] num_pts: {0:d}".format(num_pts))
    if num_pts == 0:
        return

    ## Create segmentation geometry points and line connectivity.
    #
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_pts)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(num_pts+1)
    n = 0
    for pt in coords:
        points.SetPoint(n, pt[0], pt[1], pt[2])
        lines.InsertCellPoint(n)
        n += 1
    #_for pt in coords
    lines.InsertCellPoint(0)

    geom = vtk.vtkPolyData()
    geom.SetPoints(points)
    geom.SetLines(lines)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(2.0)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    renderer.AddActor(actor)

    ## Add center point.
    #
    if show_center:
        center = segmentation.get_center()
        #print("gr.create_segmentation_geometry] Center: {0:g} {1:g} {2:g}".format(center[0], center[1], center[2]))
        num_pts = 1
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        pid = points.InsertNextPoint(center)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pid)
        points_pd = vtk.vtkPolyData()
        points_pd.SetPoints(points)
        points_pd.SetVerts(vertices)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(points_pd)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        renderer.AddActor(actor)
        actor.GetProperty().SetPointSize(5)
        renderer.AddActor(actor)

    ## Add control points.
    #
    if show_cpts:
        try:
            coords = segmentation.get_control_points()
        except:
            coords = []
        num_pts = len(coords)
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in coords:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        #_for pt in coords
        points_pd = vtk.vtkPolyData()
        points_pd.SetPoints(points)
        points_pd.SetVerts(vertices)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(points_pd)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        actor.GetProperty().SetPointSize(5)
        renderer.AddActor(actor)

def create_path_geometry(renderer, path, line_color=[0.0, 0.6, 0.0], marker_color=[1.0,0.0,0.0], show_points=False):
    ''' Create geometry for the path curve and control points.
    '''
    coords = path.get_curve_points()
    num_pts = len(coords)

    # Create contour geometry points and line connectivity.
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_pts)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(num_pts)
    n = 0
    for pt in coords:
        points.SetPoint(n, pt[0], pt[1], pt[2])
        lines.InsertCellPoint(n)
        n += 1
    #_for pt in coords

    geom = vtk.vtkPolyData()
    geom.SetPoints(points)
    geom.SetLines(lines)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(2.0)
    actor.GetProperty().SetColor(line_color[0], line_color[1], line_color[2])
    renderer.AddActor(actor)

    ## Show curve points.
    if show_points:
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in coords:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        #_for pt in coords
        points_pd = vtk.vtkPolyData()
        points_pd.SetPoints(points)
        points_pd.SetVerts(vertices)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(points_pd)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.0, 0.0, 1.0)
        actor.GetProperty().SetPointSize(5)
        renderer.AddActor(actor)

    ## Add control points.
    coords = path.get_control_points()
    num_pts = len(coords)
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    for pt in coords:
        pid = points.InsertNextPoint(pt)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pid)
    #_for pt in coords
    points_pd = vtk.vtkPolyData()
    points_pd.SetPoints(points)
    points_pd.SetVerts(vertices)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(points_pd)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(marker_color[0], marker_color[1], marker_color[2])
    actor.GetProperty().SetPointSize(8)
    renderer.AddActor(actor)

#_create_path_geometry(renderer, path)

def convert_ug_to_polydata(mesh):
    '''
    Convert mesh to polydata.
    '''
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputData(mesh)
    geometry_filter.Update()
    mesh_polydata = geometry_filter.GetOutput()

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputData(mesh_polydata)
    triangle_filter.Update()
    polydata = triangle_filter.GetOutput()
    return polydata 

def create_contour_geometry(renderer, contour):
    """ Create geometry for the contour points and control points.
    """
    coords = contour.get_points()
    num_pts = len(coords)

    ## Create contour geometry points and line connectivity.
    #
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_pts)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(num_pts+1)
    n = 0
    for pt in coords:
        points.SetPoint(n, pt[0], pt[1], pt[2])
        lines.InsertCellPoint(n)
        n += 1
    #_for pt in coords
    lines.InsertCellPoint(0)

    geom = vtk.vtkPolyData()
    geom.SetPoints(points)
    geom.SetLines(lines)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(2.0)
    actor.GetProperty().SetColor(0.0, 0.6, 0.0)
    renderer.AddActor(actor)

    ## Add center point.
    #
    center = contour.get_center()
    num_pts = 1
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    pid = points.InsertNextPoint(center)
    vertices.InsertNextCell(1)
    vertices.InsertCellPoint(pid)
    points_pd = vtk.vtkPolyData()
    points_pd.SetPoints(points)
    points_pd.SetVerts(vertices)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(points_pd)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 0.0, 0.0)
    actor.GetProperty().SetPointSize(5)
    renderer.AddActor(actor)

    ## Add control points.
    #
    try:
        coords = contour.get_control_points()
        num_pts = len(coords)
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in coords:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        #_for pt in coords
        points_pd = vtk.vtkPolyData()
        points_pd.SetPoints(points)
        points_pd.SetVerts(vertices)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(points_pd)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        actor.GetProperty().SetPointSize(5)
    except:
        pass
    # renderer.AddActor(actor)

def display(renderer_win):
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_win)
    # Set the window title.
    renderer_win.Render()
    renderer_win.SetWindowName("SV Python API")
    interactor.Start()

def add_geometry(renderer, polydata, color=[1.0, 1.0, 1.0], wire=False, edges=False):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarVisibility(False)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    #actor.GetProperty().SetPointSize(5)

    if wire:
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetLineWidth(1.0)
    elif not edges:
        actor.GetProperty().SetLineWidth(2.0)

    if edges:
        actor.GetProperty().EdgeVisibilityOn();
    else:
        actor.GetProperty().EdgeVisibilityOff();

    renderer.AddActor(actor)

def add_plane(renderer, center, normal, color=[1.0, 1.0, 1.0], wire=False):
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetCenter(center);
    planeSource.SetNormal(normal)
    planeSource.Update()
    plane_pd = planeSource.GetOutput()
    add_geometry(renderer, plane_pd, color, wire)

def add_sphere(renderer, center, radius, color=[1.0, 1.0, 1.0], wire=False):
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(center[0], center[1], center[2])
    sphere.SetRadius(radius) 
    sphere.SetPhiResolution(16)
    sphere.SetThetaResolution(16)
    sphere.Update()
    sphere_pd = sphere.GetOutput() 
    add_geometry(renderer, sphere_pd, color, wire)

def init_graphics(win_width, win_height):
    ''' Create renderer and graphics window.
    '''
    renderer = vtk.vtkRenderer()
    renderer_win = vtk.vtkRenderWindow()
    renderer_win.AddRenderer(renderer)
    renderer.SetBackground(0.8, 0.8, 0.8)
    renderer_win.SetSize(win_width, win_height)
    #renderer_win.Render()
    #renderer_win.SetWindowName("SV Python API")
    return renderer, renderer_win 